const form = document.getElementById("registration-form");
const alertBox = document.getElementById("form-alert");
const submitBtn = document.getElementById("submit-btn");

function showAlert(message, type = "success") {
  alertBox.textContent = message;
  alertBox.className = `alert alert-${type} show`;
}

function clearFieldErrors() {
  document.querySelectorAll(".field-error").forEach((el) => {
    el.textContent = "";
  });
}

function setFieldError(fieldName, message) {
  const errorEl = document.querySelector(`[data-error-for="${fieldName}"]`);
  if (errorEl) {
    errorEl.textContent = message;
  }
}

function validateForm(data) {
  clearFieldErrors();
  let isValid = true;

  if (!data.full_name || data.full_name.length < 2) {
    setFieldError("full_name", "Please enter your full name.");
    isValid = false;
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!data.email || !emailPattern.test(data.email)) {
    setFieldError("email", "Please enter a valid email address.");
    isValid = false;
  }

  const phoneDigits = data.phone.replace(/\D/g, "");
  if (!data.phone || phoneDigits.length < 10) {
    setFieldError("phone", "Please enter a valid phone number.");
    isValid = false;
  }

  if (!data.college || data.college.length < 2) {
    setFieldError("college", "Please enter your college name.");
    isValid = false;
  }

  if (data.github_url) {
    try {
      new URL(data.github_url);
    } catch {
      setFieldError("github_url", "Please enter a valid URL.");
      isValid = false;
    }
  }

    // Team size must be between 2 and 4
    if (data.team_size === null || isNaN(data.team_size) || data.team_size < 2 || data.team_size > 4) {
      setFieldError("team_size", "Please select a team size between 2 and 4.");
      isValid = false;
    }

  return isValid;
}

function getFormData() {
  const formData = new FormData(form);
  return {
    full_name: formData.get("full_name").trim(),
    email: formData.get("email").trim(),
    phone: formData.get("phone").trim(),
    college: formData.get("college").trim(),
      college_id: formData.get("college_id") ? formData.get("college_id").trim() : "",
    branch: formData.get("branch").trim(),
      team_name: formData.get("team_name") ? formData.get("team_name").trim() : "",
      team_size: formData.get("team_size") ? parseInt(formData.get("team_size"), 10) : null,
    year: formData.get("year"),
    skills: formData.get("skills").trim(),
    github_url: formData.get("github_url").trim(),
      tshirt_size: formData.get("tshirt_size") || "",
  };
}

async function handleSubmit(event) {
  event.preventDefault();
  alertBox.className = "alert";

  const payload = getFormData();
  if (!validateForm(payload)) {
    showAlert("Please fix the highlighted errors before submitting.", "error");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting...";

  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...payload,
          branch: payload.branch || null,
          year: payload.year || null,
          skills: payload.skills || null,
          github_url: payload.github_url || null,
          college_id: payload.college_id || null,
          team_name: payload.team_name || null,
          team_size: payload.team_size || null,
          tshirt_size: payload.tshirt_size || null,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      const message =
        typeof result.detail === "string"
          ? result.detail
          : "Registration failed. Please try again.";
      showAlert(message, "error");
      return;
    }

    form.reset();
    showAlert("Registration successful! We look forward to seeing you at the hackathon.", "success");
  } catch {
    showAlert("Unable to connect to the server. Please try again later.", "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Registration";
  }
}

if (form) {
  form.addEventListener("submit", handleSubmit);
}
