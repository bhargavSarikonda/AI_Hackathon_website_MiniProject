const otpForm = document.getElementById("otp-form");
const alertBox = document.getElementById("login-alert");
const emailInput = document.getElementById("email");
const mobileInput = document.getElementById("mobile");
const otpInput = document.getElementById("otp");
const sendOtpBtn = document.getElementById("send-otp-btn");

function showAlert(message, type = "success") {
  alertBox.textContent = message;
  alertBox.className = `alert alert-${type} show`;
}

function generateOtp() {
  return String(Math.floor(100000 + Math.random() * 900000));
}

function saveOtp(otp, email) {
  sessionStorage.setItem("hackathon_user_email", email);
  sessionStorage.setItem("hackathon_otp", otp);
}

function validateInputs() {
  const email = emailInput.value.trim();
  const mobile = mobileInput.value.trim();
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(email)) {
    showAlert("Please enter a valid registered email.", "error");
    return false;
  }

  if (mobile.length < 10) {
    showAlert("Please enter a valid mobile number.", "error");
    return false;
  }

  return { email, mobile };
}

sendOtpBtn.addEventListener("click", () => {
  const valid = validateInputs();
  if (!valid) return;

  const otp = generateOtp();
  saveOtp(otp, valid.email);

  showAlert(`OTP sent successfully to ${valid.email}. Demo OTP: ${otp}`, "success");
  otpInput.focus();
});

if (otpForm) {
  otpForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const email = emailInput.value.trim();
    const mobile = mobileInput.value.trim();
    const enteredOtp = otpInput.value.trim();
    const savedOtp = sessionStorage.getItem("hackathon_otp");

    if (!email || !mobile) {
      showAlert("Please enter your registered email and mobile number.", "error");
      return;
    }

    if (!enteredOtp || enteredOtp.length !== 6) {
      showAlert("Please enter the 6-digit OTP.", "error");
      return;
    }

    if (savedOtp && enteredOtp === savedOtp) {
      sessionStorage.setItem("hackathon_logged_in", "true");
      sessionStorage.setItem("hackathon_user_email", email);
      window.location.href = "user-dashboard.html";
      return;
    }

    showAlert("Invalid OTP. Please try again.", "error");
  });
}
