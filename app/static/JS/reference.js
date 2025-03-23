// DOM Elements
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menu-toggle');
const chatContainer = document.getElementById('chat-container');
const welcomeScreen = document.getElementById('welcome-screen');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const exampleCards = document.querySelectorAll('.example-card');
const newChatBtn = document.querySelector('.new-chat-btn');

// Toggle sidebar on mobile
menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('show');
});

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    
    // Enable/disable send button based on content
    sendButton.disabled = this.value.trim() === '';
});

// Handle Enter key press (send message on Enter, new line on Shift+Enter)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendButton.disabled) {
            sendMessage();
        }
    }
});

// Send message function
async function sendMessage() {
    const question = messageInput.value.trim();
    if (question === '') return;
    
    // Hide welcome screen if visible
    if (welcomeScreen && welcomeScreen.style.display !== 'none') {
        welcomeScreen.style.display = 'none';
    }
    
    // Add user message to chat
    addMessage(question, 'user');
    
    // Clear input and reset height
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    // In a real application, you would send the message to your Flask backend here
    const response = await fetch('/api/teleData',{
        method: 'POST',
        body: JSON.stringify({question: question}),
        headers: {
            'Content-Type': 'application/json'
        }
    })

    const data = await response.json();
    console.log(data);




    // For this demo, we'll simulate a response after a delay
    setTimeout(() => {
        // Hide typing indicator
        hideTypingIndicator();
        
        // Generate a response based on the message
        let botResponse = getBotResponse(question);
        
        // Add bot response to chat
        addMessage(botResponse, 'bot');
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
}

// Handle send button click
sendButton.addEventListener('click', sendMessage);

// Add message to chat
function addMessage(text, sender) {
    // Create message elements
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender + '-message');
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('message-avatar');
    
    if (sender === 'user') {
        avatarDiv.classList.add('user-avatar-chat');
        avatarDiv.textContent = 'U';
    } else {
        avatarDiv.classList.add('bot-avatar');
        avatarDiv.textContent = 'A';
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    const textDiv = document.createElement('div');
    textDiv.classList.add('message-text');
    
    // Process text for markdown-like formatting
    // For simplicity, we'll just wrap paragraphs and handle code blocks
    const formattedText = formatMessageText(text);
    textDiv.innerHTML = formattedText;
    
    const actionsDiv = document.createElement('div');
    actionsDiv.classList.add('message-actions');
    
    // Add copy button for bot messages
    if (sender === 'bot') {
        const copyButton = document.createElement('button');
        copyButton.classList.add('action-button');
        copyButton.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5" stroke="currentColor" stroke-width="2"/>
            </svg>
            Copy
        `;
        copyButton.addEventListener('click', () => {
            // Copy the plain text content
            navigator.clipboard.writeText(text);
            copyButton.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Copied!
            `;
            setTimeout(() => {
                copyButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                        <path d="M5 15H4C2.89543 15 2 14.1046 2 13V4C2 2.89543 2.89543 2 4 2H13C14.1046 2 15 2.89543 15 4V5" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Copy
                `;
            }, 2000);
        });
        actionsDiv.appendChild(copyButton);
    }
    
    // Build message structure
    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(actionsDiv);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    // Add to chat container
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add to history if it's a user message (in a real app)
    if (sender === 'user') {
        // This would integrate with your Flask backend
        // For demo purposes, we'll just log it
        console.log('Message to send to backend:', text);
    }
}

// Formatting function for message text
function formatMessageText(text) {
    // Split by double newlines to get paragraphs
    const paragraphs = text.split(/\n\n+/);
    
    // Process each paragraph
    return paragraphs.map(para => {
        // Handle code blocks (simple implementation)
        if (para.includes('```')) {
            return para.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        }
        
        // Handle inline code
        para = para.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Wrap in paragraph tags if not a code block
        if (!para.includes('<pre>')) {
            return `<p>${para}</p>`;
        }
        
        return para;
    }).join('');
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot-message');
    typingDiv.id = 'typing-indicator-message';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('message-avatar', 'bot-avatar');
    avatarDiv.textContent = 'A';
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    const typingIndicator = document.createElement('div');
    typingIndicator.classList.add('typing-indicator');
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    contentDiv.appendChild(typingIndicator);
    typingDiv.appendChild(avatarDiv);
    typingDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator-message');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Generate a bot response (in a real app, this would come from your Flask backend)
function getBotResponse(message) {
    // Simple response generator for demo
    if (message.toLowerCase().includes('python')) {
        return "Python is a great choice for many applications. Here's a simple example:\n\n```python\ndef analyze_data(data):\n    results = {}\n    # Process the data\n    for item in data:\n        # Your analysis logic here\n        pass\n    return results\n```\n\nYou can adapt this function to your specific needs. Would you like more specific guidance?";
    } else if (message.toLowerCase().includes('database') || message.toLowerCase().includes('schema')) {
        return "For a blog database schema, you'll typically need these core tables:\n\n1. Users - Store user information (id, username, email, password_hash, etc.)\n2. Posts - Store blog posts (id, title, content, user_id, created_at, etc.)\n3. Categories - Store post categories (id, name, description)\n4. Tags - Store post tags (id, name)\n5. Comments - Store comments on posts (id, content, user_id, post_id, created_at)\n\nYou'll also need junction tables for many-to-many relationships like post_tags.\n\nWould you like me to elaborate on any specific table design?";
    } else if (message.toLowerCase().includes('quantum')) {
        return "Quantum computing in simple terms:\n\nClassical computers use bits (0s and 1s). Quantum computers use quantum bits or 'qubits'.\n\nThe key differences:\n\n1. Qubits can exist in multiple states at once (superposition)\n2. Qubits can be 'entangled' with each other, creating connected systems\n\nThis allows quantum computers to explore many solutions simultaneously, making them potentially much faster for certain problems like factoring large numbers or simulating quantum physics systems.\n\nHowever, quantum computers are still experimental and face challenges with error rates and stability.";
    } else if (message.toLowerCase().includes('email') || message.toLowerCase().includes('deadline')) {
        return "Here's a professional email requesting a deadline extension:\n\nSubject: Request for Deadline Extension - [Project Name]\n\nDear [Recipient Name],\n\nI hope this email finds you well. I'm writing regarding the [Project Name] deadline currently set for [Current Deadline].\n\nDue to [brief explanation of circumstances], I would like to request an extension to [Proposed New Deadline]. This additional time would allow me to [explain benefit - e.g., \"incorporate important feedback\" or \"ensure the highest quality deliverable\"].\n\nI understand the importance of this project and its timeline. I've already completed [mention progress made] and have a clear plan to complete the remaining work by the proposed new date.\n\nPlease let me know if the extension is possible or if you'd like to discuss alternative arrangements.\n\nThank you for your consideration.\n\nBest regards,\n[Your Name]";
    } else {
        return "I'm your AI assistant, ready to help with information, tasks, or creative work. I can explain complex topics, write code, design systems, draft content, answer questions, or just have a conversation.\n\nSome things I can help with:\n- Coding and technical questions\n- Learning and explaining concepts\n- Writing and communication tasks\n- Planning and organization\n- Creative brainstorming\n\nWhat would you like assistance with today?";
    }
}

// Handle example card clicks
exampleCards.forEach(card => {
    card.addEventListener('click', () => {
        const prompt = card.getAttribute('data-prompt');
        if (prompt) {
            messageInput.value = prompt;
            // Trigger height adjustment
            messageInput.dispatchEvent(new Event('input'));
            // Focus the input
            messageInput.focus();
        }
    });
});

// New chat button functionality
newChatBtn.addEventListener('click', () => {
    // Clear chat
    while (chatContainer.firstChild) {
        chatContainer.removeChild(chatContainer.firstChild);
    }
    chatContainer.appendChild(welcomeScreen);
    // Show welcome screen
    if (welcomeScreen) {
        welcomeScreen.style.display = 'flex';
    }
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    
    // On mobile, close the sidebar
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('show');
    }
    
    // In a real application, you would also notify your Flask backend to start a new chat session
});

// Click on history item (for demo)
document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', () => {
        // Show a sample conversation for demonstration
        // In a real app, this would load the conversation from your backend
        
        // Clear chat
        while (chatContainer.firstChild) {
            chatContainer.removeChild(chatContainer.firstChild);
        }
        
        // Hide welcome screen
        // Hide welcome screen
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
        
        // Add sample messages for demonstration
        const historyTitle = item.querySelector('.history-title').textContent;
        
        // Add user message
        if (historyTitle.includes('database')) {
            addMessage("Can you help me design a database schema for a blog?", 'user');
            addMessage(getBotResponse("Can you help me design a database schema for a blog?"), 'bot');
        } else if (historyTitle.includes('Python')) {
            addMessage("What's a good way to analyze data in Python?", 'user');
            addMessage(getBotResponse("What's a good way to analyze data in Python?"), 'bot');
        } else if (historyTitle.includes('email')) {
            addMessage("Can you draft an email requesting a deadline extension?", 'user');
            addMessage(getBotResponse("Can you draft an email requesting a deadline extension?"), 'bot');
        } else {
            addMessage("Tell me about quantum computing in simple terms.", 'user');
            addMessage(getBotResponse("Tell me about quantum computing in simple terms."), 'bot');
        }
        
        // On mobile, close the sidebar
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('show');
        }
    });
});

// Initialize the UI
window.addEventListener('DOMContentLoaded', () => {
    // Disable send button initially
    sendButton.disabled = true;
    
    // Focus the input field (but not on mobile devices)
    if (window.innerWidth > 768) {
        messageInput.focus();
    }
    
    // Additional initialization if needed
    console.log('Chat UI initialized');
});

// Handle window resize events
window.addEventListener('resize', () => {
    // If window is resized to desktop size and sidebar was hidden, show it
    if (window.innerWidth > 768) {
        sidebar.classList.add('show');
    } else {
        // On mobile view, hide sidebar by default
        sidebar.classList.remove('show');
    }
});