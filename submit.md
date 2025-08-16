<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Submit Your Fintech Challenge</title>
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
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0a192f 0%, #172a45 100%);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            max-width: 800px;
            padding: 0 20px;
        }
        
        .header h1 {
            color: var(--text-light);
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00f7ff, #00b4cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .header p {
            color: rgba(255, 255, 255, 0.85);
            font-size: 1.1rem;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .container {
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: var(--card-shadow);
            width: 100%;
            max-width: 800px;
            padding: 40px;
            position: relative;
            overflow: hidden;
            margin-bottom: 30px;
        }
        
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 6px;
            background: linear-gradient(90deg, #00f7ff, #00b4cc);
        }
        
        .form-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .form-header h2 {
            color: var(--dark);
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .form-header p {
            color: #666;
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
        }
        
        .form-group label i {
            margin-right: 10px;
            color: #00b4cc;
            font-size: 1.1rem;
        }
        
        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 14px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1rem;
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
        
        .form-group input:hover,
        .form-group textarea:hover,
        .form-group select:hover {
            border-color: #a0a0a0;
        }
        
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        
        .checkbox-group {
            display: flex;
            align-items: flex-start;
            margin-top: 10px;
        }
        
        .checkbox-group input {
            width: auto;
            margin-right: 10px;
            margin-top: 5px;
        }
        
        .checkbox-group label {
            font-weight: normal;
            margin-bottom: 0;
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .status.success {
            background: rgba(40, 167, 69, 0.1);
            color: var(--success);
            display: block;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }
        
        .status.error {
            background: rgba(220, 53, 69, 0.1);
            color: var(--error);
            display: block;
            border: 1px solid rgba(220, 53, 69, 0.3);
        }
        
        .submit-btn {
            background: linear-gradient(135deg, #00f7ff, #00b4cc);
            color: white;
            border: none;
            padding: 16px 30px;
            font-size: 1.1rem;
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
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .submit-btn i {
            margin-right: 8px;
        }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            max-width: 800px;
            padding: 0 20px;
            font-size: 0.9rem;
        }
        
        .footer a {
            color: #00f7ff;
            text-decoration: none;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .form-header h2 {
                font-size: 1.5rem;
            }
            
            .submit-btn {
                padding: 14px 20px;
                font-size: 1rem;
            }
        }
        
        @media (max-width: 480px) {
            body {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
            
            .container {
                padding: 25px 15px;
            }
            
            .form-group input,
            .form-group textarea,
            .form-group select {
                padding: 12px;
            }
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
        
        .error-message {
            color: var(--error);
            font-size: 0.85rem;
            margin-top: 5px;
            display: none;
        }
        
        .form-group.invalid .error-message {
            display: block;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-lightbulb"></i> Submit Your Fintech Challenge</h1>
        <p>Help build Africa's next-generation AI solutions by sharing your fintech problems</p>
    </div>
    
    <div class="container">
        <div class="form-header">
            <h2>Share Your Challenge</h2>
            <p>Describe the problem you're facing in detail. Our community will help create innovative solutions.</p>
        </div>
        
        <div id="form-status" class="status"></div>
        
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
    
    <div class="footer">
        <p>Your submission will help drive innovation in African fintech. By submitting, you agree to our <a href="#">privacy policy</a>.</p>
        <p>© 2025 OpenLabs AI. All rights reserved.</p>
    </div>

    <script>
        const form = document.getElementById('problem-form');
        const formStatus = document.getElementById('form-status');
        const formGroups = document.querySelectorAll('.form-group');
        
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
                    
                    if (error) {
                        error.style.display = 'block';
                    }
                } else if (input.type === 'email' && !validateEmail(input.value)) {
                    group.classList.add('invalid');
                    isValid = false;
                    
                    if (error) {
                        error.textContent = 'Please enter a valid email address';
                        error.style.display = 'block';
                    }
                } else {
                    if (error) {
                        error.style.display = 'none';
                    }
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
                formStatus.className = 'status error';
                return;
            }
            
            // Show loading state
            formStatus.textContent = 'Submitting your challenge...';
            formStatus.className = 'status';
            formStatus.style.display = 'block';
            
            // Get form data
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            // Simulate submission (in real implementation, you'd connect to Google Apps Script)
            setTimeout(() => {
                // Show success message
                form.reset();
                formStatus.textContent = 'Thank you! Your challenge has been submitted to our solution pipeline.';
                formStatus.className = 'status success';
                
                // Add a slight delay before scrolling to the status
                setTimeout(() => {
                    formStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
            }, 1500);
        });
        
        // Add real-time validation
        formGroups.forEach(group => {
            const input = group.querySelector('input, textarea, select');
            
            if (input) {
                input.addEventListener('input', () => {
                    if (input.value) {
                        group.classList.remove('invalid');
                        const error = group.querySelector('.error-message');
                        if (error) error.style.display = 'none';
                    }
                });
                
                input.addEventListener('change', () => {
                    if (input.value) {
                        group.classList.remove('invalid');
                        const error = group.querySelector('.error-message');
                        if (error) error.style.display = 'none';
                    }
                });
            }
        });
    </script>
</body>
</html>
