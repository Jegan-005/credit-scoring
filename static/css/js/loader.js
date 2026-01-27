// ===== CREDX AI LOADER & UTILITIES =====

// Loading Animation Controller
class LoadingController {
  constructor() {
    this.steps = [
      'Validating financial information',
      'Running AI credit analysis', 
      'Calculating risk assessment',
      'Generating personalized report'
    ];
    this.currentStep = 0;
    this.progressBar = null;
    this.stepElements = [];
  }

  init() {
    this.progressBar = document.querySelector('.progress-fill');
    this.stepElements = document.querySelectorAll('.step');
    this.startLoading();
  }

  startLoading() {
    // Start progress bar animation
    if (this.progressBar) {
      this.progressBar.style.width = '0%';
      setTimeout(() => {
        this.progressBar.style.width = '100%';
      }, 100);
    }

    // Activate steps sequentially
    this.activateNextStep();
  }

  activateNextStep() {
    if (this.currentStep < this.stepElements.length) {
      this.stepElements[this.currentStep].classList.add('active');
      this.currentStep++;
      
      if (this.currentStep < this.stepElements.length) {
        setTimeout(() => this.activateNextStep(), 600);
      } else {
        // All steps complete, redirect to dashboard
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 800);
      }
    }
  }
}

// Credit Score Animation
class CreditScoreAnimator {
  constructor(targetScore, element) {
    this.targetScore = targetScore;
    this.element = element;
    this.currentScore = 300;
    this.animationSpeed = 20;
  }

  animate() {
    const increment = Math.ceil((this.targetScore - this.currentScore) / 20);
    
    const animation = setInterval(() => {
      if (this.currentScore < this.targetScore) {
        this.currentScore += increment;
        if (this.currentScore > this.targetScore) {
          this.currentScore = this.targetScore;
        }
        this.element.textContent = this.currentScore;
      } else {
        this.element.textContent = this.targetScore;
        clearInterval(animation);
        this.addPulseEffect();
      }
    }, this.animationSpeed);
  }

  addPulseEffect() {
    this.element.style.animation = 'pulse 2s ease-in-out 3';
  }
}

// Dashboard Utilities
class DashboardUtils {
  static formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  static formatNumber(number) {
    return new Intl.NumberFormat('en-IN').format(number);
  }

  static calculateEMI(principal, rate, tenure) {
    const monthlyRate = rate / 12 / 100;
    const months = tenure * 12;
    
    const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, months)) / 
                (Math.pow(1 + monthlyRate, months) - 1);
    
    return {
      emi: Math.round(emi),
      totalAmount: Math.round(emi * months),
      totalInterest: Math.round((emi * months) - principal)
    };
  }

  static getRiskColor(score) {
    if (score >= 750) return 'success';
    if (score >= 650) return 'warning';
    return 'danger';
  }

  static getRiskLevel(score) {
    if (score >= 750) return 'Low';
    if (score >= 650) return 'Medium';
    return 'High';
  }

  static getInterestRateRange(riskLevel) {
    switch (riskLevel) {
      case 'Low': return '8.5% - 11.5%';
      case 'Medium': return '11.5% - 15.5%';
      case 'High': return '15.5% - 22%';
      default: return '12% - 18%';
    }
  }
}

// Chatbot Controller
class ChatbotController {
  constructor() {
    this.isOpen = false;
    this.messageHistory = [];
    this.typingTimeout = null;
  }

  init() {
    this.bindEvents();
    this.showWelcomeMessage();
  }

  bindEvents() {
    const chatBtn = document.getElementById('chatbotBtn');
    const chatInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    if (chatBtn) {
      chatBtn.addEventListener('click', () => this.toggle());
    }

    if (chatInput) {
      chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.sendMessage();
        }
      });
    }

    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendMessage());
    }

    // Suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const message = btn.textContent.trim();
        this.sendSuggestion(message);
      });
    });
  }

  toggle() {
    const chatbot = document.getElementById('chatbot');
    const notification = document.getElementById('chatNotification');
    
    this.isOpen = !this.isOpen;
    
    if (this.isOpen) {
      chatbot.classList.add('show');
      if (notification) notification.style.display = 'none';
    } else {
      chatbot.classList.remove('show');
    }
  }

  showWelcomeMessage() {
    // Welcome message is already in HTML
  }

  sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;

    this.addMessage(message, 'user');
    input.value = '';
    
    this.showTyping();
    
    fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: message})
    })
    .then(res => res.json())
    .then(data => {
      this.hideTyping();
      this.addMessage(data.reply, 'bot');
    })
    .catch(error => {
      this.hideTyping();
      this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    });
  }

  sendSuggestion(message) {
    document.getElementById('userInput').value = message;
    this.sendMessage();
  }

  addMessage(message, sender) {
    const chatBody = document.getElementById('chatBody');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-msg' : 'bot-msg';
    
    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    messageDiv.innerHTML = `<i class="${icon}"></i> ${message}`;
    
    chatBody.appendChild(messageDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
    
    // Add to history
    this.messageHistory.push({message, sender, timestamp: new Date()});
  }

  showTyping() {
    const chatBody = document.getElementById('chatBody');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'bot-msg typing';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<i class="fas fa-robot"></i> <span class="typing-dots">Thinking<span>.</span><span>.</span><span>.</span></span>';
    chatBody.appendChild(typingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  hideTyping() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
  }
}

// Form Validation Utilities
class FormValidator {
  static validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  static validateAge(age) {
    return age >= 18 && age <= 80;
  }

  static validateIncome(income) {
    return income >= 10000;
  }

  static validatePassword(password) {
    return password.length >= 6;
  }

  static showError(element, message) {
    element.style.borderColor = '#ff4757';
    
    // Remove existing error message
    const existingError = element.parentNode.querySelector('.error-text');
    if (existingError) existingError.remove();
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-text';
    errorDiv.style.color = '#ff4757';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '5px';
    errorDiv.textContent = message;
    element.parentNode.appendChild(errorDiv);
  }

  static clearError(element) {
    element.style.borderColor = '';
    const errorText = element.parentNode.querySelector('.error-text');
    if (errorText) errorText.remove();
  }
}

// Notification System
class NotificationSystem {
  static show(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fas fa-${this.getIcon(type)}"></i>
      <span>${message}</span>
      <button class="notification-close">&times;</button>
    `;
    
    // Style the notification
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      background: this.getBackgroundColor(type),
      color: 'white',
      padding: '15px 20px',
      borderRadius: '8px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      zIndex: '10000',
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      minWidth: '300px',
      animation: 'slideInRight 0.3s ease-out'
    });
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
      this.remove(notification);
    }, duration);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
      this.remove(notification);
    });
  }

  static getIcon(type) {
    switch (type) {
      case 'success': return 'check-circle';
      case 'error': return 'exclamation-triangle';
      case 'warning': return 'exclamation-circle';
      default: return 'info-circle';
    }
  }

  static getBackgroundColor(type) {
    switch (type) {
      case 'success': return 'linear-gradient(135deg, #2eff7a, #06d755)';
      case 'error': return 'linear-gradient(135deg, #ff4757, #ff3742)';
      case 'warning': return 'linear-gradient(135deg, #ffc107, #ff8f00)';
      default: return 'linear-gradient(135deg, #00e5ff, #2196f3)';
    }
  }

  static remove(notification) {
    notification.style.animation = 'slideOutRight 0.3s ease-in';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }
}

// Local Storage Manager
class StorageManager {
  static set(key, value) {
    try {
      localStorage.setItem(`credx_${key}`, JSON.stringify(value));
    } catch (e) {
      console.warn('LocalStorage not available:', e);
    }
  }

  static get(key) {
    try {
      const item = localStorage.getItem(`credx_${key}`);
      return item ? JSON.parse(item) : null;
    } catch (e) {
      console.warn('LocalStorage not available:', e);
      return null;
    }
  }

  static remove(key) {
    try {
      localStorage.removeItem(`credx_${key}`);
    } catch (e) {
      console.warn('LocalStorage not available:', e);
    }
  }

  static clear() {
    try {
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith('credx_')) {
          localStorage.removeItem(key);
        }
      });
    } catch (e) {
      console.warn('LocalStorage not available:', e);
    }
  }
}

// Initialize based on page
document.addEventListener('DOMContentLoaded', function() {
  // Loading page
  if (document.querySelector('.loading-container')) {
    const loader = new LoadingController();
    loader.init();
  }

  // Dashboard page
  if (document.querySelector('.dashboard-container')) {
    // Initialize chatbot
    const chatbot = new ChatbotController();
    chatbot.init();

    // Animate credit score
    const scoreElement = document.querySelector('.score-number');
    if (scoreElement) {
      const targetScore = parseInt(scoreElement.textContent);
      const animator = new CreditScoreAnimator(targetScore, scoreElement);
      animator.animate();
    }

    // Initialize tooltips and other dashboard features
    initializeDashboardFeatures();
  }

  // Auth pages
  if (document.querySelector('.auth-form')) {
    initializeAuthValidation();
  }
});

// Dashboard Features
function initializeDashboardFeatures() {
  // EMI Calculator
  window.calculateEMI = function() {
    const principal = parseFloat(document.getElementById('loanAmount').value);
    const rate = parseFloat(document.getElementById('interestRate').value);
    const tenure = parseFloat(document.getElementById('tenure').value);
    
    if (!principal || !rate || !tenure) {
      NotificationSystem.show('Please fill all fields', 'error');
      return;
    }
    
    const result = DashboardUtils.calculateEMI(principal, rate, tenure);
    
    document.getElementById('emiResult').innerHTML = `
      <div class="emi-results">
        <div class="result-item">
          <span class="label">Monthly EMI:</span>
          <span class="value">${DashboardUtils.formatCurrency(result.emi)}</span>
        </div>
        <div class="result-item">
          <span class="label">Total Interest:</span>
          <span class="value">${DashboardUtils.formatCurrency(result.totalInterest)}</span>
        </div>
        <div class="result-item">
          <span class="label">Total Amount:</span>
          <span class="value">${DashboardUtils.formatCurrency(result.totalAmount)}</span>
        </div>
      </div>
    `;
  };

  // Quick Actions
  window.openLoanCalculator = function() {
    document.getElementById('loanModal').style.display = 'block';
  };

  window.closeLoanCalculator = function() {
    document.getElementById('loanModal').style.display = 'none';
  };

  window.downloadReport = function() {
    window.location.href = '/download-report';
  };

  window.shareScore = function() {
    if (navigator.share) {
      navigator.share({
        title: 'My CredX AI Credit Score',
        text: 'Check out my credit score analysis on CredX AI!',
        url: window.location.href
      });
    } else {
      NotificationSystem.show('Sharing not supported on this device', 'warning');
    }
  };

  window.scheduleReview = function() {
    window.location.href = '/schedule-review';
  };
}

// Auth Validation
function initializeAuthValidation() {
  const form = document.querySelector('.auth-form');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    let isValid = true;

    // Email validation
    const emailInput = form.querySelector('input[name="email"]');
    if (emailInput) {
      if (!FormValidator.validateEmail(emailInput.value)) {
        FormValidator.showError(emailInput, 'Please enter a valid email address');
        isValid = false;
      } else {
        FormValidator.clearError(emailInput);
      }
    }

    // Age validation
    const ageInput = form.querySelector('input[name="age"]');
    if (ageInput) {
      const age = parseInt(ageInput.value);
      if (!FormValidator.validateAge(age)) {
        FormValidator.showError(ageInput, 'Age must be between 18 and 80');
        isValid = false;
      } else {
        FormValidator.clearError(ageInput);
      }
    }

    // Income validation
    const incomeInput = form.querySelector('input[name="income"]');
    if (incomeInput) {
      const income = parseInt(incomeInput.value);
      if (!FormValidator.validateIncome(income)) {
        FormValidator.showError(incomeInput, 'Minimum income requirement: ₹10,000');
        isValid = false;
      } else {
        FormValidator.clearError(incomeInput);
      }
    }

    // Password validation
    const passwordInput = form.querySelector('input[name="password"]');
    if (passwordInput) {
      if (!FormValidator.validatePassword(passwordInput.value)) {
        FormValidator.showError(passwordInput, 'Password must be at least 6 characters');
        isValid = false;
      } else {
        FormValidator.clearError(passwordInput);
      }
    }

    // Confirm password validation
    const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
    if (confirmPasswordInput && passwordInput) {
      if (confirmPasswordInput.value !== passwordInput.value) {
        FormValidator.showError(confirmPasswordInput, 'Passwords do not match');
        isValid = false;
      } else {
        FormValidator.clearError(confirmPasswordInput);
      }
    }

    if (!isValid) {
      e.preventDefault();
    }
  });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
  
  .error-text {
    animation: fadeIn 0.3s ease-out;
  }
`;
document.head.appendChild(style);

// Export for global use
window.CredXUtils = {
  DashboardUtils,
  ChatbotController,
  FormValidator,
  NotificationSystem,
  StorageManager,
  CreditScoreAnimator,
  LoadingController
};