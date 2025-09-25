// auth-validation.js - Validation du formulaire d'inscription

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signup-form');
    const inputs = form.querySelectorAll('input, select');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    // Configuration des règles de validation
    const validationRules = {
        prenom: {
            pattern: /^[a-zA-ZÀ-ÿ\s-]{2,50}$/,
            message: 'Le prénom doit contenir entre 2 et 50 caractères alphabétiques'
        },
        nom: {
            pattern: /^[a-zA-ZÀ-ÿ\s-]{2,50}$/,
            message: 'Le nom doit contenir entre 2 et 50 caractères alphabétiques'
        },
        email: {
            pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            message: 'Veuillez entrer une adresse email valide'
        },
        site: {
            pattern: /.+/,
            message: 'Veuillez sélectionner un site'
        },
        departement: {
            pattern: /.+/,
            message: 'Veuillez sélectionner un département'
        },
        password1: {
            pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
            message: 'Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial'
        },
        password2: {
            pattern: /.+/,
            message: 'Veuillez confirmer votre mot de passe'
        }
    };

    // État de validation des champs
    const fieldStates = {};

    // Initialisation
    inputs.forEach(input => {
        fieldStates[input.name] = false;
        setupFieldValidation(input);
    });

    // Configuration de la validation pour chaque champ
    function setupFieldValidation(input) {
        const fieldName = input.name;
        
        // Validation en temps réel
        input.addEventListener('input', function() {
            validateField(this);
            updateProgress();
        });

        // Validation à la perte de focus
        input.addEventListener('blur', function() {
            validateField(this, true);
        });

        // Validation initiale si le champ est pré-rempli
        if (input.value.trim() !== '') {
            validateField(input);
        }
    }

    // Validation d'un champ spécifique
    function validateField(field, showError = false) {
        const fieldName = field.name;
        const value = field.value.trim();
        const rules = validationRules[fieldName];
        const errorElement = document.getElementById(`error-${fieldName}`) || createErrorElement(field);

        let isValid = false;
        let errorMessage = '';

        // Validation basique - champ requis
        if (!rules) {
            isValid = value.length > 0;
            errorMessage = isValid ? '' : 'Ce champ est obligatoire';
        } else {
            // Validation avec pattern
            isValid = rules.pattern.test(value);
            errorMessage = isValid ? '' : rules.message;

            // Validation spéciale pour l'email
            if (fieldName === 'email' && isValid) {
                isValid = validateEmailDomain(value);
                if (!isValid) {
                    errorMessage = 'Le domaine email n\'est pas autorisé';
                }
            }

            // Validation spéciale pour la confirmation de mot de passe
            if (fieldName === 'password2' && isValid) {
                const password1 = form.querySelector('input[name="password1"]').value;
                isValid = value === password1;
                errorMessage = isValid ? '' : 'Les mots de passe ne correspondent pas';
            }

            // Validation spéciale pour le mot de passe (force)
            if (fieldName === 'password1' && isValid) {
                const strength = checkPasswordStrength(value);
                updatePasswordStrengthIndicator(strength);
            }
        }

        // Mise à jour de l'état du champ
        fieldStates[fieldName] = isValid;

        // Mise à jour de l'apparence du champ
        updateFieldAppearance(field, isValid, showError);

        // Affichage des messages d'erreur
        if (showError || (!isValid && value.length > 0)) {
            showErrorMessages(field, errorMessage, errorElement);
        } else {
            hideErrorMessages(errorElement);
        }

        return isValid;
    }

    // Validation du domaine email
    function validateEmailDomain(email) {
        const allowedDomains = [
            'sah-analytics.admin',
            'sah-analytics.prestataire', 
            'sah-analytics.secretaire',
            // Ajouter d'autres domaines autorisés ici
        ];

        const domain = email.split('@')[1];
        return allowedDomains.some(allowedDomain => 
            domain === allowedDomain || domain.endsWith('.' + allowedDomain)
        );
    }

    // Vérification de la force du mot de passe
    function checkPasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[@$!%*?&]/.test(password)) strength++;

        return strength;
    }

    // Mise à jour de l'indicateur de force du mot de passe
    function updatePasswordStrengthIndicator(strength) {
        let indicator = document.getElementById('password-strength');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'password-strength';
            indicator.className = 'mt-2 text-xs font-medium';
            const passwordField = form.querySelector('input[name="password1"]');
            passwordField.parentNode.appendChild(indicator);
        }

        const strengths = {
            0: { text: 'Très faible', color: 'text-red-600' },
            1: { text: 'Faible', color: 'text-red-500' },
            2: { text: 'Moyen', color: 'text-yellow-500' },
            3: { text: 'Bon', color: 'text-yellow-600' },
            4: { text: 'Fort', color: 'text-green-500' },
            5: { text: 'Très fort', color: 'text-green-600' }
        };

        const currentStrength = strengths[strength] || strengths[0];
        indicator.innerHTML = `Force du mot de passe: <span class="${currentStrength.color}">${currentStrength.text}</span>`;
    }

    // Mise à jour de l'apparence du champ
    function updateFieldAppearance(field, isValid, showError) {
        field.classList.remove('border-green-500', 'border-red-500', 'shake');
        
        if (field.value.trim() === '') {
            field.classList.remove('border-green-500', 'border-red-500');
        } else if (isValid) {
            field.classList.add('border-green-500');
            field.classList.remove('border-red-500');
        } else if (showError || field.value.trim() !== '') {
            field.classList.add('border-red-500');
            field.classList.remove('border-green-500');
            
            if (showError && !isValid) {
                field.classList.add('shake');
                setTimeout(() => field.classList.remove('shake'), 500);
            }
        }
    }

    // Affichage des messages d'erreur
    function showErrorMessages(field, message, errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    // Masquage des messages d'erreur
    function hideErrorMessages(errorElement) {
        errorElement.style.display = 'none';
    }

    // Création d'un élément d'erreur
    function createErrorElement(field) {
        const errorElement = document.createElement('p');
        errorElement.className = 'mt-2 text-sm text-red-600 flex items-center error-message';
        errorElement.id = `error-${field.name}`;
        errorElement.style.display = 'none';
        
        errorElement.innerHTML = `
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
            </svg>
            <span></span>
        `;
        
        field.parentNode.appendChild(errorElement);
        return errorElement;
    }

    // Mise à jour de la barre de progression
    function updateProgress() {
        const totalFields = Object.keys(fieldStates).length;
        const validFields = Object.values(fieldStates).filter(state => state).length;
        const progress = Math.round((validFields / totalFields) * 100);

        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;

        // Animation de la barre de progression
        if (progress === 100) {
            progressBar.classList.add('progress-complete');
        } else {
            progressBar.classList.remove('progress-complete');
        }
    }

    // Gestionnaire de bascule de visibilité des mots de passe
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.closest('.relative').querySelector('input');
            const icon = this.querySelector('svg');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />';
            } else {
                input.type = 'password';
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />';
            }
        });
    });

    // Validation du formulaire avant soumission
    form.addEventListener('submit', function(e) {
        let isFormValid = true;
        
        // Validation de tous les champs
        inputs.forEach(input => {
            if (!validateField(input, true)) {
                isFormValid = false;
            }
        });

        if (!isFormValid) {
            e.preventDefault();
            
            // Animation d'erreur
            form.classList.add('shake');
            setTimeout(() => form.classList.remove('shake'), 500);
            
            // Scroll vers la première erreur
            const firstError = form.querySelector('.border-red-500');
            if (firstError) {
                firstError.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
        }
    });

    // Animation de chargement pour la soumission
    const submitButton = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function() {
        if (this.checkValidity()) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Création du compte...';
        }
    });

    // Initialisation de la progression
    updateProgress();
});

// Styles CSS supplémentaires pour les animations
const style = document.createElement('style');
style.textContent = `
    .shake {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .progress-complete {
        background: linear-gradient(45deg, #10b981, #3b82f6, #10b981);
        background-size: 200% 200%;
        animation: gradient-shift 2s ease infinite;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .error-message {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    input:valid {
        border-color: #10b981 !important;
    }
    
    input:invalid:not(:focus):not(:placeholder-shown) {
        border-color: #ef4444 !important;
    }
`;

document.head.appendChild(style);