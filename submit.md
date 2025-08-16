---
layout: page
title: Submit Your Fintech Challenge
description: Help build Africa's next-generation AI solutions by sharing your fintech problems
---

<div class="container" style="max-width: 800px; margin: 2rem auto; padding: 2rem; background: #1a1a1a; border-radius: 8px; box-shadow: 0 0 20px rgba(0,0,0,0.3); color: #e6e6e6;">
  <h1 style="color: #00f7ff; text-align: center; margin-bottom: 2rem;">Submit Your Fintech AI Challenge</h1>
  
  <div id="form-status" class="status"></div>
  
  <form id="problem-form">
    <div class="form-group">
      <label for="name">Full Name *</label>
      <input type="text" id="name" name="name" required style="background: #2a2a2a; color: #fff; border: 1px solid #333;">
    </div>
    
    <div class="form-group">
      <label for="email">Email Address *</label>
      <input type="email" id="email" name="email" required style="background: #2a2a2a; color: #fff; border: 1px solid #333;">
    </div>
    
    <div class="form-group">
      <label for="organization">Organization</label>
      <input type="text" id="organization" name="organization" style="background: #2a2a2a; color: #fff; border: 1px solid #333;">
    </div>
    
    <div class="form-group">
      <label for="problem-type">Problem Category *</label>
      <select id="problem-type" name="problem-type" required style="background: #2a2a2a; color: #fff; border: 1px solid #333;">
        <option value="">Select category</option>
        <option value="fraud">Fraud Detection</option>
        <option value="credit">Credit Scoring</option>
        <option value="payments">Payment Processing</option>
        <option value="compliance">Regulatory Compliance</option>
        <option value="npl">Natural Language Processing</option>
        <option value="other">Other</option>
      </select>
    </div>
    
    <div class="form-group">
      <label for="problem">Describe Your Problem *</label>
      <textarea id="problem" name="problem" required style="background: #2a2a2a; color: #fff; border: 1px solid #333; min-height: 150px;"></textarea>
      <p style="font-size: 0.9rem; color: #aaa;">Be specific: What pain points are you experiencing? What data do you have? What outcomes do you want?</p>
    </div>
    
    <div class="form-group">
      <label for="impact">Potential Impact *</label>
      <select id="impact" name="impact" required style="background: #2a2a2a; color: #fff; border: 1px solid #333;">
        <option value="">Select impact level</option>
        <option value="individual">Individual User</option>
        <option value="sme">Small Business</option>
        <option value="enterprise">Enterprise Level</option>
        <option value="national">National Impact</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>
        <input type="checkbox" id="consent" name="consent" required style="margin-right: 8px;">
        I consent to share this problem publicly for community solving
      </label>
    </div>
    
    <button type="submit" style="background: linear-gradient(135deg, #00f7ff, #00b4cc); color: #0a192f; padding: 12px 30px; border: none; border-radius: 4px; font-weight: bold; font-size: 1rem; display: block; width: 100%; margin-top: 1rem; cursor: pointer;">Submit Challenge</button>
  </form>
</div>

<style>
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }
  
  input, textarea, select {
    width: 100%;
    padding: 0.8rem;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  .status {
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    display: none;
  }
  
  .status.success {
    background: rgba(40, 167, 69, 0.2);
    color: #28a745;
    display: block;
    border: 1px solid #28a745;
  }
  
  .status.error {
    background: rgba(220, 53, 69, 0.2);
    color: #dc3545;
    display: block;
    border: 1px solid #dc3545;
  }
</style>

<script>
  const form = document.getElementById('problem-form');
  const formStatus = document.getElementById('form-status');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading state
    formStatus.textContent = 'Submitting...';
    formStatus.className = 'status';
    formStatus.style.display = 'block';
    
    // Get form data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
  // Send to Google Sheet
  const response = await fetch('https://script.google.com/macros/s/AKfycbystH6LmEWwqsLRbQ22GtYDrW0LrkMbrSMz3kKwN1Q2diUKTK2NaTQrhzWYiZl8uaV1/exec', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  if (response.ok) {
    form.reset();
    formStatus.textContent = 'Thank you! Your challenge has been submitted to our solution pipeline.';
    formStatus.className = 'status success';
  } else {
    throw new Error('Form submission failed');
  }
} catch (error) {
  formStatus.textContent = 'Oops! There was a problem. Please try again or contact hello@openlabs.ai';
  formStatus.className = 'status error';
  console.error(error);
}
</script>
