document.addEventListener('DOMContentLoaded', () => {
    
    // --- Navbar Scroll Effect ---
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            navbar.classList.add('shadow-md', 'py-2');
            navbar.classList.remove('py-4', 'border-transparent');
        } else {
            navbar.classList.remove('shadow-md', 'py-2');
            navbar.classList.add('py-4');
        }
    });

    // --- Mobile Menu Toggle ---
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const closeMenuBtn = document.getElementById('close-menu');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    function toggleMenu() {
        if (mobileMenu.classList.contains('translate-x-full')) {
            mobileMenu.classList.remove('translate-x-full');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        } else {
            mobileMenu.classList.add('translate-x-full');
            document.body.style.overflow = '';
        }
    }

    mobileMenuBtn.addEventListener('click', toggleMenu);
    closeMenuBtn.addEventListener('click', toggleMenu);
    
    mobileLinks.forEach(link => {
        link.addEventListener('click', toggleMenu);
    });

    // --- Scroll Reveal Animations ---
    const revealElements = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right');

    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Run once
            }
        });
    }, revealOptions);

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });

    // --- Animated Counters ---
    const counters = document.querySelectorAll('.counter');
    let hasAnimated = false; // Prevent re-animating

    const animateCounters = () => {
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText.replace(/,/g, '');
                
                // Divisor for speed (higher is slower)
                const speed = 200;
                const inc = target / speed;

                if (count < target) {
                    counter.innerText = Math.ceil(count + inc).toLocaleString();
                    setTimeout(updateCount, 10);
                } else {
                    counter.innerText = target.toLocaleString() + (target > 1000 ? '+' : '');
                }
            };
            updateCount();
        });
    };

    // Observe stats section to trigger counter animation
    const statsSection = document.getElementById('impact');
    if(statsSection) {
        const statsObserver = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && !hasAnimated) {
                hasAnimated = true;
                animateCounters();
            }
        }, { threshold: 0.5 });
        
        statsObserver.observe(statsSection);
    }

    // --- Floating Chatbot Logic ---
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotWindow = document.getElementById('chatbot-window');
    const closeChatBtn = document.getElementById('close-chat');
    const chatbotForm = document.getElementById('chatbot-form');
    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotMessages = document.getElementById('chatbot-messages');

    if (chatbotToggle && chatbotWindow && closeChatBtn && chatbotForm && chatbotInput && chatbotMessages) {
        
        function toggleChat() {
            if (chatbotWindow.classList.contains('hidden')) {
                chatbotWindow.classList.remove('hidden');
                // Trigger reflow to apply transition
                void chatbotWindow.offsetWidth;
                chatbotWindow.classList.remove('scale-95', 'opacity-0');
                chatbotWindow.classList.add('scale-100', 'opacity-100', 'flex');
            } else {
                chatbotWindow.classList.remove('scale-100', 'opacity-100', 'flex');
                chatbotWindow.classList.add('scale-95', 'opacity-0');
                setTimeout(() => {
                    chatbotWindow.classList.add('hidden');
                }, 300);
            }
        }

        chatbotToggle.addEventListener('click', toggleChat);
        closeChatBtn.addEventListener('click', toggleChat);

        chatbotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatbotInput.value.trim();
            if (!message) return;

            // Add User message
            chatbotMessages.innerHTML += `
                <div class="flex items-start gap-3 flex-row-reverse">
                    <div class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center flex-shrink-0 shadow-sm"><i class="fa-solid fa-user text-xs"></i></div>
                    <div class="bg-brand-600 p-3 rounded-2xl rounded-tr-none shadow-sm text-white leading-relaxed">
                        ${message}
                    </div>
                </div>
            `;
            chatbotInput.value = '';
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

            // Typing indicator
            const typingId = 'typing-' + Date.now();
            chatbotMessages.innerHTML += `
                <div id="${typingId}" class="flex items-start gap-3">
                    <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center flex-shrink-0 shadow-sm"><i class="fa-solid fa-robot"></i></div>
                    <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-gray-200 shadow-sm text-gray-500 italic">
                        <span class="flex gap-1 items-center h-4">
                            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                            <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                        </span>
                    </div>
                </div>
            `;
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });
                const data = await response.json();
                
                document.getElementById(typingId).remove();
                
                // Add AI response
                chatbotMessages.innerHTML += `
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center flex-shrink-0 shadow-sm"><i class="fa-solid fa-robot"></i></div>
                        <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-gray-200 shadow-sm text-gray-800 leading-relaxed">
                            ${(data.reply || 'Sorry, I encountered an error.').replace(/\\n/g, '<br>')}
                        </div>
                    </div>
                `;
            } catch(err) {
                document.getElementById(typingId).remove();
                chatbotMessages.innerHTML += `
                    <div class="flex items-start gap-3">
                        <div class="w-8 h-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0 shadow-sm"><i class="fa-solid fa-triangle-exclamation"></i></div>
                        <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-red-200 shadow-sm text-red-600">
                            Network error. Please try again.
                        </div>
                    </div>
                `;
            }
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        });
    }
});
