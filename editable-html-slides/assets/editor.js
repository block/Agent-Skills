/* editor.js — self-contained WYSIWYG layer for claude-edit-skill
 * No dependencies. Coexists with html-ppt runtime.js (presenter mode).
 *
 * Inline text edit · add image (data URL) / text box · drag / resize / delete ·
 * UNDO / REDO (snapshot stack) · FILMSTRIP reorder (slot-fixed, content-swap so
 * the presenter runtime's cached page order is never disturbed) ·
 * localStorage autosave + restore · export clean standalone HTML.
 * Toggle with E or the ✎ button. */
(function () {
  "use strict";

  var params = new URLSearchParams(location.search);
  if (params.has("preview")) { document.body.classList.add("is-preview"); return; }

  var TEXT_SEL = "h1,h2,h3,h4,p,li,blockquote,.kicker,.lede,.t,.d";
  var KEY = "cesk2::" + location.pathname;   // v2 storage (payload snapshots)
  var MAX_HISTORY = 80;

  var slots = [];          // .slide elements, FIXED DOM order (never moved)
  var sel = null;          // selected .ed-obj
  var drag = null;
  var saveTimer = null;
  var hist = [];           // array of JSON snapshot strings
  var hi = -1;             // history pointer

  /* ---------- tiny helpers ---------- */
  function $(s, c) { return (c || document).querySelector(s); }
  function activeSlot() { return $(".slide.is-active") || slots[0]; }
  function slotPos(el) { return slots.indexOf(el); }
  function clsClean(node) {
    return (node.className || "").split(/\s+/)
      .filter(function (c) { return c && c !== "is-active" && c !== "sel"; }).join(" ");
  }

  function sanitizeHTML(slot) {
    var c = slot.cloneNode(true);
    c.querySelectorAll("[contenteditable]").forEach(function (n) { n.removeAttribute("contenteditable"); });
    c.querySelectorAll("[data-ed-text]").forEach(function (n) { n.removeAttribute("data-ed-text"); });
    c.querySelectorAll(".ed-handle,.ed-del").forEach(function (n) { n.remove(); });
    c.querySelectorAll(".ed-obj").forEach(function (n) { n.classList.remove("sel", "editing-text"); n.removeAttribute("contenteditable"); });
    return c.innerHTML;
  }
  function payloadOf(slot) {
    return { cls: clsClean(slot), title: slot.getAttribute("data-title") || "", html: sanitizeHTML(slot) };
  }
  function applyPayload(slot, p) {
    var active = slot.classList.contains("is-active");
    slot.className = p.cls + (active ? " is-active" : "");
    if (p.title != null) slot.setAttribute("data-title", p.title);
    slot.innerHTML = p.html;
    markSlide(slot);
    if (isOn()) setEditableIn(slot, true);
  }
  function snapshot() { return slots.map(payloadOf); }

  /* ---------- history ---------- */
  function record() {
    var s = JSON.stringify(snapshot());
    if (s === hist[hi]) return;            // no real change
    hist = hist.slice(0, hi + 1);
    hist.push(s); hi++;
    if (hist.length > MAX_HISTORY) { hist.shift(); hi--; }
    persist(s);
    updateUndoBtns();
  }
  function restore(jsonStr) {
    var arr = JSON.parse(jsonStr);
    arr.forEach(function (p, k) { if (slots[k]) applyPayload(slots[k], p); });
    deselect();
    if (filmOpen) buildFilm();
    updateUndoBtns();
  }
  function undo() { if (hi > 0) { hi--; restore(hist[hi]); persist(hist[hi]); toast("已撤销"); } }
  function redo() { if (hi < hist.length - 1) { hi++; restore(hist[hi]); persist(hist[hi]); toast("已重做"); } }
  function persist(s) { try { localStorage.setItem(KEY, s); } catch (e) {} }
  function recordDebounced() { clearTimeout(saveTimer); saveTimer = setTimeout(record, 700); }

  /* ---------- text marking ---------- */
  function markSlide(slot) {
    slot.querySelectorAll(TEXT_SEL).forEach(function (el) {
      if (el.closest("aside.notes")) return;
      if (el.closest(".ed-obj")) return;
      el.setAttribute("data-ed-text", "");
    });
  }
  function setEditableIn(slot, on) {
    slot.querySelectorAll("[data-ed-text]").forEach(function (el) {
      if (on) el.setAttribute("contenteditable", "true");
      else el.removeAttribute("contenteditable");
    });
  }
  function setEditable(on) { slots.forEach(function (s) { setEditableIn(s, on); }); }

  /* ---------- edit mode ---------- */
  function isOn() { return document.body.classList.contains("ed-on"); }
  function toggleEdit(force) {
    var on = (force === undefined) ? !isOn() : force;
    document.body.classList.toggle("ed-on", on);
    setEditable(on);
    if (!on) { deselect(); closeFilm(); }
    launch.textContent = on ? "✓ 完成编辑" : "✎ 编辑";
    if (on) toast("编辑模式：点字改 · 加图/拖动 · ⌘Z 撤销 · 页序可拖");
  }

  /* ---------- objects ---------- */
  function ensureRelative(slot) { if (getComputedStyle(slot).position === "static") slot.style.position = "relative"; }
  function placeCenter(slot, w) {
    return { left: Math.max(20, (slot.clientWidth - w) / 2), top: Math.max(20, (slot.clientHeight - w * 0.62) / 2) };
  }
  function addImage(dataURL) {
    var slot = activeSlot(); ensureRelative(slot);
    var w = Math.min(460, slot.clientWidth * 0.4), p = placeCenter(slot, w);
    var o = document.createElement("div");
    o.className = "ed-obj ed-img";
    o.style.left = p.left + "px"; o.style.top = p.top + "px"; o.style.width = w + "px";
    o.innerHTML = '<img src="' + dataURL + '" alt="">';
    slot.appendChild(o); selectObj(o); record(); toast("已添加图片，可拖动 / 拖右下角缩放");
  }
  function addTextBox() {
    var slot = activeSlot(); ensureRelative(slot);
    var p = placeCenter(slot, 280);
    var o = document.createElement("div");
    o.className = "ed-obj ed-textbox";
    o.style.left = p.left + "px"; o.style.top = p.top + "px"; o.style.width = "280px";
    o.textContent = "双击编辑文字";
    slot.appendChild(o); selectObj(o); record();
  }
  function selectObj(o) {
    deselect(); sel = o; o.classList.add("sel");
    var h = document.createElement("div"); h.className = "ed-handle"; o.appendChild(h);
    var d = document.createElement("button"); d.className = "ed-del"; d.textContent = "✕"; o.appendChild(d);
  }
  function deselect() {
    if (!sel) return;
    sel.querySelectorAll(".ed-handle,.ed-del").forEach(function (n) { n.remove(); });
    sel.classList.remove("sel"); sel = null;
  }
  function removeSel() { if (!sel) { return; } sel.remove(); sel = null; record(); }

  /* ---------- pointer drag / resize ---------- */
  document.addEventListener("mousedown", function (e) {
    if (!isOn()) return;
    var obj = e.target.closest(".ed-obj");
    if (!obj) { if (!e.target.closest("#ed-bar") && !e.target.closest("#ed-film")) deselect(); return; }
    if (obj.classList.contains("editing-text")) return;
    if (e.target.classList.contains("ed-del")) { removeSel(); e.preventDefault(); return; }
    selectObj(obj);
    var resizing = e.target.classList.contains("ed-handle");
    var r = obj.getBoundingClientRect();
    drag = { obj: obj, resizing: resizing, x: e.clientX, y: e.clientY,
      left: parseFloat(obj.style.left) || 0, top: parseFloat(obj.style.top) || 0, w: r.width };
    e.preventDefault();
  });
  document.addEventListener("mousemove", function (e) {
    if (!drag) return;
    var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (drag.resizing) drag.obj.style.width = Math.max(40, drag.w + dx) + "px";
    else { drag.obj.style.left = (drag.left + dx) + "px"; drag.obj.style.top = (drag.top + dy) + "px"; }
  });
  document.addEventListener("mouseup", function () { if (drag) { drag = null; record(); } });

  document.addEventListener("dblclick", function (e) {
    if (!isOn()) return;
    var tb = e.target.closest(".ed-obj.ed-textbox");
    if (!tb) return;
    tb.classList.add("editing-text"); tb.setAttribute("contenteditable", "true"); tb.focus();
  });
  document.addEventListener("focusout", function (e) {
    var tb = e.target.closest && e.target.closest(".ed-obj.ed-textbox");
    if (tb) { tb.classList.remove("editing-text"); tb.removeAttribute("contenteditable"); record(); }
  });
  document.addEventListener("input", function (e) {
    if (!isOn()) return;
    if (e.target.closest("[data-ed-text]") || e.target.closest(".ed-obj")) recordDebounced();
  });
  document.addEventListener("paste", function (e) {
    if (!isOn()) return;
    if (document.activeElement && document.activeElement.isContentEditable) return;
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") === 0) {
        var rd = new FileReader(); rd.onload = function () { addImage(rd.result); };
        rd.readAsDataURL(items[i].getAsFile()); e.preventDefault(); break;
      }
    }
  });

  /* ---------- keyboard: shield runtime + shortcuts ---------- */
  window.addEventListener("keydown", function (e) {
    if (!isOn()) return;
    var k = e.key.toLowerCase();
    if ((e.metaKey || e.ctrlKey) && k === "z") { e.preventDefault(); e.stopImmediatePropagation(); if (e.shiftKey) redo(); else undo(); return; }
    if ((e.metaKey || e.ctrlKey) && k === "y") { e.preventDefault(); e.stopImmediatePropagation(); redo(); return; }
    if ((e.metaKey || e.ctrlKey) && k === "s") { e.preventDefault(); e.stopImmediatePropagation(); exportHTML(); return; }
    if (e.key === "Escape") { if (sel) deselect(); else toggleEdit(false); e.stopImmediatePropagation(); return; }
    var typing = document.activeElement && document.activeElement.isContentEditable;
    if ((e.key === "Delete" || (e.key === "Backspace" && !typing)) && sel) {
      removeSel(); e.preventDefault(); e.stopImmediatePropagation(); return;
    }
    var nav = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " ", "PageUp", "PageDown", "Home", "End"];
    var letters = ["f", "s", "t", "a", "o", "n", "r"];
    if (nav.indexOf(e.key) >= 0 || letters.indexOf(k) >= 0) e.stopImmediatePropagation();
  }, true);

  /* ---------- navigation ---------- */
  function curN() { return slotPos(activeSlot()) + 1; }
  function goto(n) {
    n = Math.max(1, Math.min(slots.length, n));
    location.hash = "#/" + n;
    setTimeout(function () { deselect(); updatePage(); if (filmOpen) buildFilm(); }, 60);
  }
  function updatePage() { page.textContent = curN() + " / " + slots.length; }

  /* ---------- filmstrip (reorder by content-swap) ---------- */
  var filmOpen = false, filmEl = null, dragFrom = -1;
  function titleOf(slot) {
    var t = slot.getAttribute("data-title");
    var h = slot.querySelector("h1,h2,.h1,.h2");
    var txt = (h ? h.textContent : (t || "")).trim().replace(/\s+/g, " ");
    return txt.length > 22 ? txt.slice(0, 22) + "…" : (txt || t || "");
  }
  function toggleFilm() { filmOpen ? closeFilm() : openFilm(); }
  function openFilm() { filmOpen = true; buildFilm(); }
  function closeFilm() { filmOpen = false; if (filmEl) filmEl.style.display = "none"; }
  function buildFilm() {
    if (!filmEl) { filmEl = document.createElement("div"); filmEl.id = "ed-film"; document.body.appendChild(filmEl); }
    filmEl.style.display = "flex";
    filmEl.innerHTML = "";
    slots.forEach(function (slot, i) {
      var chip = document.createElement("div");
      chip.className = "ed-chip" + (i === curN() - 1 ? " cur" : "");
      chip.draggable = true; chip.dataset.i = i;
      chip.innerHTML = '<span class="ci">' + (i + 1) + '</span><span class="ct">' + (titleOf(slot) || "—") + "</span>";
      chip.addEventListener("click", function () { goto(i + 1); });
      chip.addEventListener("dragstart", function () { dragFrom = i; chip.classList.add("dragging"); });
      chip.addEventListener("dragend", function () { chip.classList.remove("dragging"); });
      chip.addEventListener("dragover", function (ev) { ev.preventDefault(); chip.classList.add("over"); });
      chip.addEventListener("dragleave", function () { chip.classList.remove("over"); });
      chip.addEventListener("drop", function (ev) { ev.preventDefault(); chip.classList.remove("over"); reorder(dragFrom, i); });
      filmEl.appendChild(chip);
    });
  }
  function reorder(from, to) {
    if (from < 0 || to < 0 || from === to) return;
    var arr = snapshot();
    var moved = arr.splice(from, 1)[0];
    arr.splice(to, 0, moved);
    arr.forEach(function (p, k) { applyPayload(slots[k], p); });
    record();
    goto(to + 1);
    toast("第 " + (from + 1) + " 页 → 第 " + (to + 1) + " 页");
  }

  /* ---------- export ---------- */
  function buildExportHTML() {
    var root = document.documentElement.cloneNode(true);
    root.querySelectorAll("#ed-launch,#ed-bar,#ed-toast,#ed-film").forEach(function (n) { n.remove(); });
    root.querySelectorAll('link[href$="editor.css"],script[src$="editor.js"]').forEach(function (n) { n.remove(); });
    root.querySelector("body").classList.remove("ed-on", "is-preview");
    root.querySelectorAll(".slide").forEach(function (s) {
      s.querySelectorAll("[contenteditable]").forEach(function (n) { n.removeAttribute("contenteditable"); });
      s.querySelectorAll("[data-ed-text]").forEach(function (n) { n.removeAttribute("data-ed-text"); });
      s.querySelectorAll(".ed-handle,.ed-del").forEach(function (n) { n.remove(); });
      s.querySelectorAll(".ed-obj").forEach(function (n) { n.classList.remove("sel", "editing-text"); });
    });
    return "<!DOCTYPE html>\n" + root.outerHTML;
  }
  function exportHTML() {
    var blob = new Blob([buildExportHTML()], { type: "text/html" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "claude-edit-skill.html";
    document.body.appendChild(a); a.click(); a.remove();
    toast("已导出 claude-edit-skill.html（含修改/图片/页序）");
  }
  function resetAll() {
    try { localStorage.removeItem(KEY); } catch (e) {}
    location.reload();
  }

  /* ---------- toast ---------- */
  var toastEl, toastTimer;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.id = "ed-toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add("show");
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2400);
  }

  /* ---------- chrome (launcher + toolbar) ---------- */
  var launch = document.createElement("button");
  launch.id = "ed-launch"; launch.textContent = "✎ 编辑";
  launch.addEventListener("click", function () { toggleEdit(); });

  var bar = document.createElement("div"); bar.id = "ed-bar";
  var page = document.createElement("span"); page.className = "ed-page";
  var undoBtn, redoBtn;
  function mkBtn(label, fn, cls) {
    var b = document.createElement("button"); b.textContent = label; if (cls) b.className = cls;
    b.addEventListener("click", fn); return b;
  }
  function sep() { var s = document.createElement("span"); s.className = "ed-sep"; return s; }
  function updateUndoBtns() {
    if (undoBtn) undoBtn.disabled = hi <= 0;
    if (redoBtn) redoBtn.disabled = hi >= hist.length - 1;
  }
  var fileInput = document.createElement("input");
  fileInput.type = "file"; fileInput.accept = "image/*"; fileInput.style.display = "none";
  fileInput.addEventListener("change", function () {
    var f = fileInput.files && fileInput.files[0]; if (!f) return;
    var rd = new FileReader(); rd.onload = function () { addImage(rd.result); };
    rd.readAsDataURL(f); fileInput.value = "";
  });

  bar.appendChild(mkBtn("‹", function () { goto(curN() - 1); }));
  bar.appendChild(page);
  bar.appendChild(mkBtn("›", function () { goto(curN() + 1); }));
  bar.appendChild(sep());
  undoBtn = mkBtn("↶ 撤销", undo); redoBtn = mkBtn("↷ 重做", redo);
  bar.appendChild(undoBtn); bar.appendChild(redoBtn);
  bar.appendChild(sep());
  bar.appendChild(mkBtn("🖼 加图片", function () { fileInput.click(); }));
  bar.appendChild(mkBtn("T 文本框", function () { addTextBox(); }));
  bar.appendChild(mkBtn("▦ 页序", toggleFilm));
  bar.appendChild(sep());
  bar.appendChild(mkBtn("↺ 还原全部", resetAll));
  bar.appendChild(mkBtn("⬇ 导出", exportHTML));
  bar.appendChild(mkBtn("✓ 完成", function () { toggleEdit(false); }, "primary"));

  /* ---------- init ---------- */
  function init() {
    // Scope to the real deck only — runtime.js clones every slide into a
    // hidden .overview grid, so a bare '.slide' selector would double-count.
    var deck = document.querySelector(".deck");
    slots = Array.prototype.slice.call((deck || document).querySelectorAll(".slide"))
      .filter(function (s) { return !s.closest(".overview"); });
    // restore saved snapshot (v2)
    var saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
    if (saved) { try { JSON.parse(saved).forEach(function (p, k) { if (slots[k]) applyPayload(slots[k], p); }); } catch (e) { saved = null; } }
    slots.forEach(markSlide);
    document.body.appendChild(launch);
    document.body.appendChild(bar);
    document.body.appendChild(fileInput);
    hist = [JSON.stringify(snapshot())]; hi = 0; updateUndoBtns();
    updatePage();
    document.addEventListener("keydown", function (e) {
      if (e.key !== "e" && e.key !== "E") return;
      var t = document.activeElement;
      if (t && (t.isContentEditable || t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
      if (!isOn()) { toggleEdit(true); e.preventDefault(); }
    });
    window.addEventListener("hashchange", function () { setTimeout(updatePage, 50); });
    document.addEventListener("keyup", function () { if (isOn()) updatePage(); });
    if (params.has("edtest")) setTimeout(runSelfTest, 200);
    if (params.has("edopen")) setTimeout(function () { toggleEdit(true); openFilm(); }, 150);
  }

  /* ---------- headless self-test (?edtest=1) ---------- */
  function runSelfTest() {
    var px = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
    try {
      toggleEdit(true);
      var slot0Title = titleOf(slots[0]);
      addTextBox(); sel.textContent = "自测文本"; record();
      addImage(px);
      sel.style.left = "300px"; sel.style.top = "200px"; record();
      var objs = activeSlot().querySelectorAll(".ed-obj").length;
      var lenAfterAdds = hist.length;
      undo();                                  // undo image move? actually undo last record
      var afterUndo = hi;
      redo();
      reorder(0, 2);                           // move slide 1 -> position 3
      var movedOk = titleOf(slots[2]) === slot0Title;
      var exp = buildExportHTML();
      var stored = localStorage.getItem(KEY) || "";
      var hasEditorScript = /<script[^>]+src=["'][^"']*editor\.js/i.test(exp);
      var ok = objs >= 2 && lenAfterAdds >= 3 && afterUndo === lenAfterAdds - 2 &&
        movedOk && exp.indexOf("data:image/png") >= 0 && exp.indexOf("ed-textbox") >= 0 &&
        !hasEditorScript && stored.indexOf("ed-obj") >= 0;
      try { localStorage.removeItem(KEY); } catch (e) {}
      document.body.setAttribute("data-edtest",
        ok ? "PASS objs=" + objs + " hist=" + lenAfterAdds + " moved=" + movedOk
           : "FAIL objs=" + objs + " hist=" + lenAfterAdds + " undo=" + afterUndo + " moved=" + movedOk);
    } catch (err) { document.body.setAttribute("data-edtest", "ERROR " + (err && err.message)); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
