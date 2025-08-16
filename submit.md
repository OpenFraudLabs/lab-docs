---
layout: page
title: Submit Your Fintech Challenge
description: Help build Africa's next-generation AI solutions by sharing your fintech problems
---

<div class="form-container">
  <div class="form-header">
    <div class="logo">
      <div class="logo-icon">
        <i class="fas fa-brain"></i>
      </div>
      <h1>OpenLabs AI</h1>
    </div>
    <h2>Submit Your Fintech Challenge</h2>
    <p>Help build Africa's next-generation AI solutions by sharing your fintech problems</p>
  </div>
  
  <div class="form-card">
    <div class="form-intro">
      <h3><i class="fas fa-lightbulb"></i> Share Your Challenge</h3>
      <p>Describe the problem you're facing in detail. Our community will help create innovative solutions.</p>
    </div>
    
    <div id="form-status" class="form-status"></div>
    
    <form id="problem-form">
      <div class="form-group">
        <label for="name"><i class="fas fa-user"></i> Full Name *</label>
        <input type="text" id="name" name="name" required>
        <div class="error-message">Please enter your full name</div>
      </div>
      
      <div class="form-group">
        <label for="email"><i class="fas fa-envelope"></i> Email Address *</label>
        <input type="email" id="email" name="email" required>
        <div class="error-message">Please enter a valid email address</div>
      </div>
      
      <div class="form-group">
        <label for="organization"><i class="fas fa-building"></i> Organization</label>
        <input type="text" id="organization" name="organization">
      </div>
      
      <div class="form-group">
        <label for="problem-type"><i class="fas fa-folder"></i> Problem Category *</label>
        <select id="problem-type" name="problem-type" required>
          <option value="">Select category</option>
          <option value="fraud">Fraud Detection</option>
          <option value="credit">Credit Scoring</option>
          <option value="payments">Payment Processing</option>
          <option value="compliance">Regulatory Compliance</option>
          <option value="npl">Natural Language Processing</option>
          <option value="other">Other</option>
        </select>
        <div class="error-message">Please select a category</div>
      </div>
      
      <div class="form-group">
        <label for="problem"><i class="fas fa-question-circle"></i> Describe Your Problem *</label>
        <textarea id="problem" name="problem" required placeholder="Be specific: What pain points are you experiencing? What data do you have? What outcomes do you want?"></textarea>
        <div class="error-message">Please describe your problem</div>
      </div>
      
      <div class="form-group">
        <label for="impact"><i class="fas fa-chart-line"></i> Potential Impact *</label>
        <select id="impact" name="impact" required>
          <option value="">Select impact level</option>
          <option value="individual">Individual User</option>
          <option value="sme">Small Business</option>
          <option value="enterprise">Enterprise Level</option>
          <option value="national">National Impact</option>
        </select>
        <div class="error-message">Please select an impact level</div>
      </div>
      
      <div class="form-group">
        <div class="checkbox-group">
          <input type="checkbox" id="consent" name="consent" required>
          <label for="consent">I consent to share this problem publicly for community solving</label>
        </div>
        <div class="error-message">Please agree to share your problem</div>
      </div>
      
      <button type="submit" class="submit-btn">
        <i class="fas fa-paper-plane"></i> Submit Challenge
      </button>
    </form>
  </div>
  
  <div class="form-footer">
    <p>Your submission will help drive innovation in African fintech. By submitting, you agree to our <a href="#">privacy policy</a>.</p>
    <p>© 2025 OpenLabs AI. All rights reserved.</p>
  </div>
</div>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
  :root {
    --primary: #0a192f;
    --secondary: #00f7ff;
    --accent: #ff2e63;
    --light: #f8f9fa;
    --dark: #0a192f;
    --text: #333;
    --text-light: #e6e6e6;
    --success: #28a745;
    --error: #dc3545;
    --card-bg: #ffffff;
    --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    --gradient: linear-gradient(135deg, #00f7ff, #00b4cc);
    --gradient-accent: linear-gradient(135deg, #ff2e63, #e01e4f);
  }
  
  .form-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 30px 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: var(--text);
  }
  
  .form-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    gap: 15px;
  }
  
  .logo-icon {
    width: 50px;
    height: 50px;
    background: var(--gradient);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .logo-icon i {
    font-size: 24px;
    color: white;
  }
  
  .logo h1 {
    font-size: 32px;
    font-weight: 700;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  
  .form-header h2 {
    font-size: 28px;
    color: var(--primary);
    margin-bottom: 10px;
  }
  
  .form-header p {
    color: #555;
    font-size: 18px;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
  }
  
  .form-card {
    background: var(--card-bg);
    border-radius: 16px;
    box-shadow: var(--card-shadow);
    padding: 40px;
    position: relative;
    overflow: hidden;
    margin-bottom: 30px;
  }
  
  .form-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: var(--gradient);
  }
  
  .form-intro {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .form-intro h3 {
    font-size: 22px;
    color: var(--primary);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
  
  .form-intro h3 i {
    color: #00b4cc;
  }
  
  .form-intro p {
    color: #666;
    font-size: 16px;
  }
  
  .form-status {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 25px;
    display: none;
    animation: fadeIn 0.5s ease;
    font-size: 16px;
  }
  
  .form-status.success {
    background: rgba(40, 167, 69, 0.1);
    color: var(--success);
    display: block;
    border: 1px solid rgba(40, 167, 69, 0.3);
  }
  
  .form-status.error {
    background: rgba(220, 53, 69, 0.1);
    color: var(--error);
    display: block;
    border: 1px solid rgba(220, 53, 69, 0.3);
  }
  
  .form-group {
    margin-bottom: 25px;
    position: relative;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #444;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 16px;
  }
  
  .form-group input,
  .form-group textarea,
  .form-group select {
    width: 100%;
    padding: 14px 15px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: all 0.3s ease;
    background: white;
  }
  
  .form-group input:focus,
  .form-group textarea:focus,
  .form-group select:focus {
    border-color: #00b4cc;
    box-shadow: 0 0 0 3px rgba(0, 183, 204, 0.2);
    outline: none;
  }
  
  textarea {
    min-height: 150px;
    resize: vertical;
  }
  
  .checkbox-group {
    display: flex;
    align-items: flex-start;
    margin-top: 10px;
    gap: 10px;
  }
  
  .checkbox-group input {
    margin-top: 5px;
  }
  
  .checkbox-group label {
    font-weight: normal;
    margin-bottom: 0;
  }
  
  .error-message {
    color: var(--error);
    font-size: 14px;
    margin-top: 5px;
    display: none;
  }
  
  .submit-btn {
    background: var(--gradient);
    color: white;
    border: none;
    padding: 16px 30px;
    font-size: 18px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: block;
    width: 100%;
    margin-top: 20px;
    box-shadow: 0 4px 15px rgba(0, 183, 204, 0.3);
    letter-spacing: 0.5px;
  }
  
  .submit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 183, 204, 0.4);
  }
  
  .submit-btn i {
    margin-right: 10px;
  }
  
  .form-footer {
    text-align: center;
    color: #666;
    font-size: 14px;
    padding: 0 20px;
  }
  
  .form-footer a {
    color: #00b4cc;
    text-decoration: none;
  }
  
  .form-footer a:hover {
    text-decoration: underline;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  /* Form validation */
  .form-group.invalid input,
  .form-group.invalid textarea,
  .form-group.invalid select {
    border-color: var(--error);
  }
  
  .form-group.invalid label {
    color: var(--error);
  }
  
  .form-group.invalid .error-message {
    display: block;
  }
  
  /* Responsive design */
  @media (max-width: 768px) {
    .form-card {
      padding: 30px;
    }
    
    .form-header h2 {
      font-size: 24px;
    }
    
    .form-header p {
      font-size: 16px;
    }
    
    .form-intro h3 {
      font-size: 20px;
    }
    
    .submit-btn {
      padding: 14px 20px;
      font-size: 16px;
    }
  }
  
  @media (max-width: 480px) {
    .form-container {
      padding: 20px 15px;
    }
    
    .form-card {
      padding: 25px 20px;
    }
    
    .logo h1 {
      font-size: 28px;
    }
    
    .form-header h2 {
      font-size: 22px;
    }
    
    .form-group input,
    .form-group textarea,
    .form-group select {
      padding: 12px;
    }
  }
</style>

<script>
  const form = document.getElementById('problem-form');
  const formStatus = document.getElementById('form-status');
  const formGroups = document.querySelectorAll('.form-group');
  
  // Google Apps Script URL
  const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxWlMrhVUgRbXM52xn88WZJMU8X9PKTSa_ot1jDqrWA7JP8jw2ECV5E0ypdSuMlpDl5/exec";
  
  // Form validation function
  function validateForm() {
    let isValid = true;
    
    formGroups.forEach(group => {
      const input = group.querySelector('input, textarea, select');
      const error = group.querySelector('.error-message');
      
      // Remove invalid class first
      group.classList.remove('invalid');
      
      // Skip organization field as it's optional
      if (input.id === 'organization') return;
      
      if (!input.value || (input.type === 'checkbox' && !input.checked)) {
        group.classList.add('invalid');
        isValid = false;
      } else if (input.type === 'email' && !validateEmail(input.value)) {
        group.classList.add('invalid');
        if (error) error.textContent = 'Please enter a valid email address';
        isValid = false;
      }
    });
    
    return isValid;
  }
  
  // Email validation function
  function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }
  
  // Form submission handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      formStatus.textContent = 'Please fill in all required fields correctly.';
      formStatus.className = 'form-status error';
      formStatus.style.display = 'block';
      return;
    }
    
    // Show loading state
    formStatus.textContent = 'Submitting your challenge...';
    formStatus.className = 'form-status';
    formStatus.style.display = 'block';
    
    // Get form data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
      // Send to Google Sheet
      const response = await fetch(GOOGLE_SCRIPT_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        // Show success message
        form.reset();
        formStatus.textContent = 'Thank you! Your challenge has been submitted to our solution pipeline.';
        formStatus.className = 'form-status success';
        
        // Add a slight delay before scrolling to the status
        setTimeout(() => {
          formStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      } else {
        throw new Error('Form submission failed');
      }
    } catch (error) {
      formStatus.textContent = 'Oops! There was a problem. Please try again or contact hello@openlabs.ai';
      formStatus.className = 'form-status error';
    }
  });
  
  // Add real-time validation
  formGroups.forEach(group => {
    const input = group.querySelector('input, textarea, select');
    
    if (input) {
      input.addEventListener('input', () => {
        if (input.value) {
          group.classList.remove('invalid');
        }
      });
      
      input.addEventListener('change', () => {
        if (input.value) {
          group.classList.remove('invalid');
        }
      });
    }
  });
</script>
