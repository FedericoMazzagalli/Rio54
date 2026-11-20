package com.federico.mazzagalli.rio54;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import android.Manifest;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Build;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

/** Device-level smoke tests for the packaged, offline HTML5 game in the Android WebView. */
@RunWith(AndroidJUnit4.class)
public final class RIO54AndroidSmokeTest {

    @Test
    public void gameLoadsFromLocalHttpsOriginWithoutInternetPermission() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            awaitPage(scenario);
            JSONObject page = new JSONObject(evaluate(scenario,
                    "({origin:location.origin,protocol:location.protocol,title:document.title," +
                    "languageOptions:Array.from(document.querySelectorAll('#languageSelect option'))" +
                    ".map(o=>o.value).filter(v=>v!=='more'),hasWebglCanvas:!!document.querySelector('#rio54WebglCanvas')," +
                    "hasServiceWorker:('serviceWorker' in navigator)})"));

            assertEquals("https://appassets.androidplatform.net", page.getString("origin"));
            assertEquals("https:", page.getString("protocol"));
            assertTrue("The RIO54 page title should be present", page.getString("title").contains("RIO54"));
            assertEquals("es,en,pt-BR,fr,de,it,ja,zh-CN", join(page.getJSONArray("languageOptions")));
            assertTrue("The WebGL canvas should be part of the packaged game", page.getBoolean("hasWebglCanvas"));
            assertTrue("Android WebView should expose the service worker API", page.getBoolean("hasServiceWorker"));

            scenario.onActivity(activity -> {
                try {
                    PackageManager pm = activity.getPackageManager();
                    PackageInfo info;
                    if (Build.VERSION.SDK_INT >= 33) {
                        info = pm.getPackageInfo(activity.getPackageName(),
                                PackageManager.PackageInfoFlags.of(PackageManager.GET_PERMISSIONS));
                    } else {
                        //noinspection deprecation
                        info = pm.getPackageInfo(activity.getPackageName(), PackageManager.GET_PERMISSIONS);
                    }
                    boolean requestsInternet = false;
                    if (info.requestedPermissions != null) {
                        for (String permission : info.requestedPermissions) {
                            if (Manifest.permission.INTERNET.equals(permission)) requestsInternet = true;
                        }
                    }
                    assertFalse("The offline APK must not request android.permission.INTERNET", requestsInternet);
                } catch (PackageManager.NameNotFoundException e) {
                    throw new AssertionError(e);
                }
            });
        }
    }

    @Test
    public void firstCaseOpensClueAndPersistsProgressAfterActivityRecreation() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            awaitPage(scenario);

            JSONObject play = new JSONObject(evaluate(scenario,
                    "(()=>{" +
                    "localStorage.clear();" +
                    "document.querySelector('#newGame').click();" +
                    "const intro=document.querySelector('#introScreen').classList.contains('active');" +
                    "document.querySelector('#beginCase').click();" +
                    "const playing=document.querySelector('#playScreen').classList.contains('active');" +
                    "const clueCount=document.querySelectorAll('#leadGrid button').length;" +
                    "document.querySelector('#leadGrid button').click();" +
                    "const modal=document.querySelector('#modalBack').classList.contains('open');" +
                    "document.querySelector('#modalChoices button').click();" +
                    "const saved=JSON.parse(localStorage.getItem('rio54_save_v1'));" +
                    "const clueSaved=saved.runs.c1.found.includes(0);" +
                    "document.querySelector('#modalDone').click();" +
                    "return {intro,playing,clueCount,modal,clueSaved,origin:location.origin};" +
                    "})()"));

            assertTrue("New Game should open the case introduction", play.getBoolean("intro"));
            assertTrue("Opening the case should enter the playable screen", play.getBoolean("playing"));
            assertEquals("The first case should contain four clues", 4, play.getInt("clueCount"));
            assertTrue("Selecting a clue should open its modal", play.getBoolean("modal"));
            assertTrue("Registering the clue should persist it in localStorage", play.getBoolean("clueSaved"));

            scenario.recreate();
            awaitPage(scenario);
            JSONObject restored = new JSONObject(evaluate(scenario,
                    "({saved:JSON.parse(localStorage.getItem('rio54_save_v1')).runs.c1.found.length," +
                    "continueEnabled:!document.querySelector('#continueTop').disabled})"));
            assertEquals("One clue should survive Activity recreation", 1, restored.getInt("saved"));
            assertTrue("Continue should become available after saving progress", restored.getBoolean("continueEnabled"));
        }
    }

    @Test
    public void serviceWorkerCanRegisterAndActivateForOfflineShell() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            awaitPage(scenario);
            evaluate(scenario,
                    "navigator.serviceWorker.ready.then(r=>localStorage.setItem(" +
                    "'__rio54_sw_test',r&&r.active?'active':'inactive'))" +
                    ".catch(()=>localStorage.setItem('__rio54_sw_test','error')); 'started'");

            String status = "pending";
            for (int i = 0; i < 40; i++) {
                status = evaluate(scenario, "localStorage.getItem('__rio54_sw_test')||'pending'")
                        .replace("\"", "");
                if ("active".equals(status) || "missing".equals(status) || "error".equals(status)) break;
                Thread.sleep(250);
            }
            assertEquals("The packaged service worker should register and activate", "active", status);

            evaluate(scenario,
                    "caches.open('rio54-static-v1.4.3').then(c=>Promise.all([" +
                    "c.match(new URL('./index.html',location.href).href)," +
                    "c.match(new URL('./narrative_translations.js',location.href).href)," +
                    "c.match(new URL('./webgl_renderer.js',location.href).href)]))" +
                    ".then(r=>localStorage.setItem('__rio54_cache_test',r.every(Boolean)?'complete':'partial'))" +
                    ".catch(()=>localStorage.setItem('__rio54_cache_test','error')); 'checking'");
            String cache = "pending";
            for (int i = 0; i < 40; i++) {
                cache = evaluate(scenario, "localStorage.getItem('__rio54_cache_test')||'pending'")
                        .replace("\"", "");
                if ("complete".equals(cache) || "partial".equals(cache) || "error".equals(cache)) break;
                Thread.sleep(250);
            }
            assertEquals("The offline cache should contain the HTML, translations and WebGL renderer",
                    "complete", cache);
        }
    }

    private static void awaitPage(ActivityScenario<MainActivity> scenario) throws Exception {
        for (int i = 0; i < 60; i++) {
            String ready = evaluate(scenario,
                    "document.readyState==='complete' && !!document.querySelector('#newGame') ? 'yes' : 'no'")
                    .replace("\"", "");
            if ("yes".equals(ready)) return;
            Thread.sleep(250);
        }
        throw new AssertionError("RIO54 did not finish loading within 15 seconds");
    }

    private static String evaluate(ActivityScenario<MainActivity> scenario, String javascript) throws Exception {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<String> value = new AtomicReference<>();
        AtomicReference<Throwable> failure = new AtomicReference<>();
        scenario.onActivity(activity -> {
            try {
                WebView webView = findWebView(activity.getWindow().getDecorView());
                assertNotNull("MainActivity must contain a WebView", webView);
                webView.evaluateJavascript(javascript, result -> {
                    value.set(result == null ? "null" : result);
                    latch.countDown();
                });
            } catch (Throwable t) {
                failure.set(t);
                latch.countDown();
            }
        });
        assertTrue("Timed out waiting for WebView JavaScript", latch.await(20, TimeUnit.SECONDS));
        if (failure.get() != null) throw new AssertionError(failure.get());
        assertNotNull("WebView JavaScript must return a value", value.get());
        return value.get();
    }

    private static WebView findWebView(View view) {
        if (view instanceof WebView) return (WebView) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                WebView found = findWebView(group.getChildAt(i));
                if (found != null) return found;
            }
        }
        return null;
    }

    private static String join(org.json.JSONArray values) throws Exception {
        StringBuilder output = new StringBuilder();
        for (int i = 0; i < values.length(); i++) {
            if (i > 0) output.append(',');
            output.append(values.getString(i));
        }
        return output.toString();
    }
}
