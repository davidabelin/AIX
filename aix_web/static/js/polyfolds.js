(function () {
  "use strict";

  const form = document.getElementById("polyfoldsJobForm");
  const kindInput = document.getElementById("kindInput");
  const solidInput = document.getElementById("solidInput");
  const countInput = document.getElementById("countInput");
  const nValidInput = document.getElementById("nValidInput");
  const nIncompleteInput = document.getElementById("nIncompleteInput");
  const nInvalidInput = document.getElementById("nInvalidInput");
  const seedInput = document.getElementById("seedInput");
  const timeoutInput = document.getElementById("timeoutInput");
  const quickInput = document.getElementById("quickInput");
  const plotInput = document.getElementById("plotInput");
  const refreshJobsBtn = document.getElementById("refreshJobsBtn");
  const jobStatus = document.getElementById("jobStatus");
  const jobDetail = document.getElementById("jobDetail");
  const jobsTableBody = document.getElementById("jobsTableBody");

  let activeJobId = null;
  let pollTimer = null;

  function setStatus(text) {
    jobStatus.textContent = text;
  }

  function payloadFromForm() {
    const kind = String(kindInput.value || "dataset").trim();
    const params = {
      seed: Number(seedInput.value || 2025),
      timeout_seconds: Number(timeoutInput.value || 900),
    };
    if (kind === "dataset") {
      params.n_valid = Number(nValidInput.value || 200);
      params.n_incomplete = Number(nIncompleteInput.value || 200);
      params.n_invalid = Number(nInvalidInput.value || 200);
      params.quick = Boolean(quickInput.checked);
      params.plot = Boolean(plotInput.checked);
    } else {
      params.count = Number(countInput.value || 6);
    }
    return {
      kind,
      solid: String(solidInput.value || "tetra").trim(),
      params,
    };
  }

  async function fetchJob(jobId) {
    const response = await fetch(`/api/v1/jobs/${encodeURIComponent(jobId)}`);
    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error || "Failed to fetch job");
    }
    return body.job;
  }

  function renderDetail(job) {
    jobDetail.textContent = JSON.stringify(job, null, 2);
  }

  async function pollActiveJob() {
    if (!activeJobId) {
      return;
    }
    try {
      const job = await fetchJob(activeJobId);
      renderDetail(job);
      setStatus(`Job ${job.id}: ${job.status}`);
      if (job.status === "completed" || job.status === "failed") {
        activeJobId = null;
        if (pollTimer) {
          window.clearInterval(pollTimer);
          pollTimer = null;
        }
      }
      await refreshJobs();
    } catch (error) {
      setStatus(`Poll error: ${String(error)}`);
    }
  }

  function renderJobsTable(jobs) {
    jobsTableBody.innerHTML = "";
    jobs.forEach((job) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${job.id}</td>
        <td>${job.status}</td>
        <td>${job.kind}</td>
        <td>${job.solid}</td>
        <td>${job.exit_code === null ? "-" : job.exit_code}</td>
        <td>${job.updated_at}</td>
      `;
      tr.addEventListener("click", () => {
        activeJobId = job.id;
        renderDetail(job);
        setStatus(`Selected job ${job.id}.`);
      });
      jobsTableBody.appendChild(tr);
    });
  }

  async function refreshJobs() {
    const response = await fetch("/api/v1/jobs?limit=50");
    const body = await response.json();
    if (!response.ok) {
      throw new Error(body.error || "Failed to fetch jobs");
    }
    renderJobsTable(body.jobs || []);
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = payloadFromForm();
    try {
      setStatus("Submitting job...");
      const response = await fetch("/api/v1/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        setStatus(`Submit failed: ${body.error || "unknown error"}`);
        return;
      }
      const job = body.job;
      activeJobId = job.id;
      renderDetail(job);
      setStatus(`Job ${job.id} queued.`);
      if (pollTimer) {
        window.clearInterval(pollTimer);
      }
      pollTimer = window.setInterval(pollActiveJob, 1200);
      await refreshJobs();
    } catch (error) {
      setStatus(`Submit failed: ${String(error)}`);
    }
  });

  refreshJobsBtn.addEventListener("click", () => {
    refreshJobs()
      .then(() => setStatus("Jobs refreshed."))
      .catch((error) => setStatus(`Refresh failed: ${String(error)}`));
  });

  refreshJobs()
    .then(() => setStatus("No active job."))
    .catch((error) => setStatus(`Initialization failed: ${String(error)}`));
})();

