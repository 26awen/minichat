custom_js = r"""
    document.addEventListener('DOMContentLoaded', function() {
        // Clear localStorage items on page load
        localStorage.removeItem('currentUserId');
        localStorage.removeItem('currentTId');

        const chatButton = document.getElementById('chat_button');
        const chatOutput = document.getElementById('chat_output');
        const chatInput = document.getElementById('chat_input');
        const continueButton = document.getElementById('continue_button');

        // Function to update chat and continue button state
        function updateButtonState() {
            const inputValue = chatInput.value.trim();
            chatButton.disabled = inputValue === '';
            continueButton.disabled = inputValue === '' || !(localStorage.getItem('currentUserId') && localStorage.getItem('currentTId'));
        }

        // Call this function initially
        updateButtonState();

        // Add event listener to chat input
        chatInput.addEventListener('input', updateButtonState);

        function handleChatSubmit(event) {
            event.preventDefault();
            
            // Check if chat is allowed
            if (chatButton.disabled) {
                console.log("Chat submit is not allowed at this time");
                return;
            }
            
            const formData = new FormData();
            formData.append('dropdown_username', document.getElementById('dropdown_username').value);
            formData.append('dropdown_clienttype', document.getElementById('dropdown_clienttype').value);

            // Get the slot content
            const slotContent = document.getElementById('slot_textarea').value;

            // Replace the placeholder in the chat input with the slot content
            let chatInputContent = chatInput.value;
            chatInputContent = chatInputContent.replace(/\{\s*\{\s*slot\s*\}\s*\}/g, slotContent);

            formData.append('chat_input', chatInputContent);
            // formData.append('response_format', 'json');  // Request JSON response

            // Clear previous chat and add the new user input
            chatOutput.value = 'You: ' + chatInputContent + '\n\nAI: ';
            chatOutput.scrollTop = chatOutput.scrollHeight;

            fetch('/chat', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                // 从 localStorage 获取存储的值，如果没有则为 null
                let currentUserId = localStorage.getItem('currentUserId');
                let currentTId = localStorage.getItem('currentTId');

                function readStream() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            chatOutput.value += '\n';
                            chatOutput.scrollTop = chatOutput.scrollHeight;
                            return;
                        }
                        
                        const chunk = decoder.decode(value);
                        // console.log('Raw chunk:', chunk);  // 输出原始chunk以进行调试
                        
                        // 分割接收到的数据为单独的JSON对象
                        const jsonLines = chunk.trim().split('\n');
                        
                        jsonLines.forEach(line => {
                            if (line.trim()) {
                                try {
                                    const jsonResponse = JSON.parse(line);
                                    
                                    // 设置或更新 user_id 和 t_id，并存储到 localStorage
                                    if (jsonResponse.user_id !== undefined) {
                                        currentUserId = jsonResponse.user_id;
                                        localStorage.setItem('currentUserId', currentUserId);
                                    }
                                    if (jsonResponse.t_id !== undefined) {
                                        currentTId = jsonResponse.t_id;
                                        localStorage.setItem('currentTId', currentTId);
                                    }

                                    // Update continue button state after each response
                                    updateButtonState();

                                    if (jsonResponse.chunk) {
                                        chatOutput.value += jsonResponse.chunk;
                                    } else if (jsonResponse.error) {
                                        chatOutput.value += '\nError: ' + jsonResponse.error + '\n';
                                    } else if (jsonResponse.final) {
                                        // chatOutput.value += '\n[Chat completed]\n';
                                        console.log(`Chat completed for user_id: ${currentUserId}, t_id: ${currentTId}`);
                                    }
                                    chatOutput.scrollTop = chatOutput.scrollHeight;
                                } catch (error) {
                                    console.error('Error parsing JSON:', error);
                                    console.log('Problematic line:', line);
                                }
                            }
                        });
                        
                        readStream();
                    });
                }

                readStream();
            })
            .catch(error => {
                console.error('Error:', error);
                chatOutput.value += 'Error occurred while fetching response.\n';
                chatOutput.scrollTop = chatOutput.scrollHeight;
            });

            // Clear the input after sending
            chatInput.value = '';
        }

        chatButton.addEventListener('click', handleChatSubmit);

        // Single event listener for keyboard shortcuts
        if (chatInput) {
            chatInput.addEventListener('keydown', function(event) {
                if (event.altKey && event.key === 'Enter') {
                    event.preventDefault();
                    handleContinueChat(event);
                } else if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                    event.preventDefault();
                    handleChatSubmit(event);
                }

            });
        } else {
            console.error("Chat input element not found");
        }

        // Modify the variable button and textarea handling
        const slotButton = document.getElementById('slot_button');
        const slotModal = document.getElementById('slot_modal');
        const slotTextarea = document.getElementById('slot_textarea');
        const closeModal = document.getElementById('close_modal');
        const insertSlotButton = document.getElementById('insert_slot_button');

        slotButton.addEventListener('click', function() {
            slotModal.style.display = 'flex';
        });

        closeModal.addEventListener('click', function() {
            slotModal.style.display = 'none';
        });

        insertSlotButton.addEventListener('click', function() {
            const chatInput = document.getElementById('chat_input');
            const cursorPos = chatInput.selectionStart;
            const textBefore = chatInput.value.substring(0, cursorPos);
            const textAfter = chatInput.value.substring(cursorPos);
            chatInput.value = textBefore + '{{ slot }}' + textAfter;
            chatInput.focus();
            chatInput.selectionStart = chatInput.selectionEnd = cursorPos + 10; // 10 is the length of '{{ slot }}'
            slotModal.style.display = 'none';
        });

        window.addEventListener('click', function(event) {
            if (event.target == slotModal) {
                slotModal.style.display = 'none';
            }
        });

        function handleContinueChat(event) {
            event.preventDefault();
            
            // Check if continue is allowed
            if (continueButton.disabled) {
                console.log("Continue chat is not allowed at this time");
                return;
            }
            
            const formData = new FormData();
            formData.append('dropdown_username', document.getElementById('dropdown_username').value);
            formData.append('dropdown_clienttype', document.getElementById('dropdown_clienttype').value);
            formData.append('t_id', localStorage.getItem('currentTId'));

            // Get the slot content
            const slotContent = document.getElementById('slot_textarea').value;

            // Replace the placeholder in the chat input with the slot content
            let chatInputContent = chatInput.value;
            chatInputContent = chatInputContent.replace(/\{\s*\{\s*slot\s*\}\s*\}/g, slotContent);

            formData.append('chat_input', chatInputContent);

            // Append the new user input to the existing chat
            chatOutput.value += '\n\nYou: ' + chatInputContent + '\n\nAI: ';
            chatOutput.scrollTop = chatOutput.scrollHeight;

            fetch('/chat', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                // 从 localStorage 获取存储的值，如果没有则为 null
                let currentUserId = localStorage.getItem('currentUserId');
                let currentTId = localStorage.getItem('currentTId');

                function readStream() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            chatOutput.value += '\n';
                            chatOutput.scrollTop = chatOutput.scrollHeight;
                            return;
                        }
                        
                        const chunk = decoder.decode(value);
                        // console.log('Raw chunk:', chunk);  // 输出原始chunk以进行调试
                        
                        // 分割接收到的数据为单独的JSON对象
                        const jsonLines = chunk.trim().split('\n');
                        
                        jsonLines.forEach(line => {
                            if (line.trim()) {
                                try {
                                    const jsonResponse = JSON.parse(line);
                                    
                                    // 设置或更新 user_id 和 t_id，并存储到 localStorage
                                    if (jsonResponse.user_id !== undefined) {
                                        currentUserId = jsonResponse.user_id;
                                        localStorage.setItem('currentUserId', currentUserId);
                                    }
                                    if (jsonResponse.t_id !== undefined) {
                                        currentTId = jsonResponse.t_id;
                                        localStorage.setItem('currentTId', currentTId);
                                    }

                                    // Update continue button state after each response
                                    updateButtonState();

                                    if (jsonResponse.chunk) {
                                        chatOutput.value += jsonResponse.chunk;
                                    } else if (jsonResponse.error) {
                                        chatOutput.value += '\nError: ' + jsonResponse.error + '\n';
                                    } else if (jsonResponse.final) {
                                        // chatOutput.value += '\n[Chat completed]\n';
                                        console.log(`Chat completed for user_id: ${currentUserId}, t_id: ${currentTId}`);
                                    }
                                    chatOutput.scrollTop = chatOutput.scrollHeight;
                                } catch (error) {
                                    console.error('Error parsing JSON:', error);
                                    console.log('Problematic line:', line);
                                }
                            }
                        });
                        
                        readStream();
                    });
                }

                readStream();
            })
            .catch(error => {
                console.error('Error:', error);
                chatOutput.value += 'Error occurred while fetching response.\n';
                chatOutput.scrollTop = chatOutput.scrollHeight;
            });

            // Clear the input after sending
            chatInput.value = '';
        }

        continueButton.addEventListener('click', handleContinueChat);
    });
"""