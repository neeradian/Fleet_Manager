/* 

    ═══════════════════════════════════════════════════════
                    FleetTrack Pro – Main JS
    ═══════════════════════════════════════════════════════ 
    

*/

/* ------------------Auto-dismiss alerts --------------- */

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".alert").forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity .5s";
      el.style.opacity = "0";
      setTimeout(function () {
        el.remove();
      }, 500);
    }, 5000);
  });
});

/* ----------------Fuel form live preview ----------------- */

// function initFuelPreview() {
//   const li = document.getElementById("id_litres_filled");
//   const pr = document.getElementById("id_price_per_litre");
//   const pt = document.getElementById("preview-total");
//   if (!li || !pr || !pt) return;
//   function update() {
//     const t = (parseFloat(li.value) || 0) * (parseFloat(pr.value) || 0);
//     pt.textContent = "₹ " + t.toFixed(2);
//   }
//   li.addEventListener("input", update);
//   pr.addEventListener("input", update);
//   update();
// }

/* ----------------Upload drag-and-drop ----------------- */

// function initUploadZone() {
//   const zone = document.querySelector(".upload-zone");
//   const fileInput = document.getElementById("id_file");
//   if (!zone || !fileInput) return;

//   zone.addEventListener("click", function () {
//     fileInput.click();
//   });

//   fileInput.addEventListener("change", function () {
//     const name = fileInput.files[0] ? fileInput.files[0].name : "";
//     const label = zone.querySelector(".file-chosen");
//     if (label) label.textContent = name || "No file chosen";
//   });

//   zone.addEventListener("dragover", function (e) {
//     e.preventDefault();
//     zone.classList.add("drag-over");
//   });
//   zone.addEventListener("dragleave", function () {
//     zone.classList.remove("drag-over");
//   });
//   zone.addEventListener("drop", function (e) {
//     e.preventDefault();
//     zone.classList.remove("drag-over");
//     if (e.dataTransfer.files.length) {
//       fileInput.files = e.dataTransfer.files;
//       const label = zone.querySelector(".file-chosen");
//       if (label) label.textContent = e.dataTransfer.files[0].name;
//     }
//   });
// }

/* ----------------Report: toggle section visibility ----------------- */

function initReportToggles() {
  document.querySelectorAll("[data-toggle-section]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = document.getElementById(btn.dataset.toggleSection);
      if (!target) return;
      const hidden = target.style.display === "none";
      target.style.display = hidden ? "" : "none";
      btn.textContent = hidden ? "▲ Hide" : "▼ Show";
    });
  });
}

/* ----------------Init all ----------------- */

document.addEventListener("DOMContentLoaded", function () {
  initFuelPreview();
  initUploadZone();
  initReportToggles();
});
