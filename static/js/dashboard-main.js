let isEditMode = false;
let currentRequestId = null;
let lastUserRequest = null;
let hasConfirmedMatches = false;

// Load data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadUserRequest();
    loadMatches();
});

async function loadUserInfo() {
    try {
        const response = await fetch('/get-user-info');
        if (response.ok) {
            const userData = await response.json();
            const userDisplayName = document.getElementById('userDisplayName');
            if (userDisplayName) {
                // Use the full name from the user data
                const fullName = userData.name || 'User';
                userDisplayName.textContent = fullName;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

async function loadUserRequest() {
    try {
        const response = await fetch('/get-requests');
        const requests = await response.json();
        
        const userRequest = requests.find(req => req.is_own);
        
        if (userRequest) {
            lastUserRequest = userRequest;
            currentRequestId = userRequest.id;
            displayUserRequest(userRequest);
            document.getElementById('noRequest').style.display = 'none';
            document.getElementById('hasRequest').style.display = 'block';
        } else {
            lastUserRequest = null;
            document.getElementById('noRequest').style.display = 'block';
            document.getElementById('hasRequest').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading user request:', error);
    }
}

async function loadMatches() {
    try {
        const response = await fetch('/get-matches');
        if (!response.ok) {
            throw new Error('Failed to load matches');
        }
        const matches = await response.json();
        // Only show confirmed matches in the Matches section
        const confirmed = matches.filter(m => m.mutually_confirmed);
        const limited = confirmed.slice(0, 5);

        // Show/hide confirmed match notice
        const confirmedMatchNotice = document.getElementById('confirmedMatchNotice');
        if (confirmedMatchNotice) {
            confirmedMatchNotice.style.display = confirmed.length > 0 ? 'block' : 'none';
        }

        hasConfirmedMatches = confirmed.length > 0;

        // Disable create request button if user has confirmed match
        const createRequestBtn = document.getElementById('createRequestBtn');
        if (createRequestBtn) {
            if (hasConfirmedMatches) {
                createRequestBtn.disabled = true;
                createRequestBtn.textContent = 'Cannot Create Request (Has Confirmed Match)';
                createRequestBtn.style.opacity = '0.6';
                createRequestBtn.style.cursor = 'not-allowed';
            } else {
                createRequestBtn.disabled = false;
                createRequestBtn.textContent = 'Create Swap Request';
                createRequestBtn.style.opacity = '1';
                createRequestBtn.style.cursor = 'pointer';
            }
        }

        // Disable edit and delete buttons if user has confirmed match
        const editRequestBtn = document.getElementById('editRequestBtn');
        const deleteRequestBtn = document.getElementById('deleteRequestBtn');
        
        if (editRequestBtn) {
            if (hasConfirmedMatches) {
                editRequestBtn.disabled = true;
                editRequestBtn.textContent = 'Cannot Edit (Has Confirmed Match)';
                editRequestBtn.style.opacity = '0.6';
                editRequestBtn.style.cursor = 'not-allowed';
            } else {
                editRequestBtn.disabled = false;
                editRequestBtn.textContent = 'Edit Request';
                editRequestBtn.style.opacity = '1';
                editRequestBtn.style.cursor = 'pointer';
            }
        }
        
        if (deleteRequestBtn) {
            if (hasConfirmedMatches) {
                deleteRequestBtn.disabled = true;
                deleteRequestBtn.textContent = 'Cannot Delete (Has Confirmed Match)';
                deleteRequestBtn.style.opacity = '0.6';
                deleteRequestBtn.style.cursor = 'not-allowed';
            } else {
                deleteRequestBtn.disabled = false;
                deleteRequestBtn.textContent = 'Delete Request';
                deleteRequestBtn.style.opacity = '1';
                deleteRequestBtn.style.cursor = 'pointer';
            }
        }

        const noMatches = document.getElementById('noMatches');
        const matchesList = document.getElementById('matchesList');
        
        if (limited.length === 0) {
            noMatches.style.display = 'block';
            matchesList.style.display = 'none';
            matchesList.innerHTML = '';
        } else {
            noMatches.style.display = 'none';
            matchesList.style.display = 'grid';
            
            matchesList.innerHTML = limited.map(m => {
                // Only show YOUR ranking badge
                const myBadge = getMyPreferenceBadge(m.my_preference_level);
                
                return `
                <div class="listing-card">
                    <div class="listing-header">
                        <div class="listing-title">Match with ${m.other_user_name}</div>
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                            ${myBadge}
                            <span style="background: rgba(76, 175, 80, 0.3); padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">Confirmed</span>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px;">
                        <div style="margin-bottom: 8px;"><strong>Match Details:</strong></div>
                        <div style="font-size: 0.9rem;">
                            • ${m.other_current_apartment} (your ${getPreferenceText(m.my_preference_level)} choice)
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 10px;">
                        <strong>They're currently at:</strong> ${m.other_current_apartment || ''}
                        ${m.other_current_room ? ` (${m.other_current_room})` : ''}
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>Their preferences:</strong><br/>
                        ${m.other_first_choice ? `1st: ${m.other_first_choice}<br/>` : ''}
                        ${m.other_second_choice ? `2nd: ${m.other_second_choice}<br/>` : ''}
                        ${m.other_third_choice ? `3rd: ${m.other_third_choice}<br/>` : ''}
                    </div>
                    <div class="contact-info" style="margin-bottom: 15px;">
                        <strong>Contact:</strong> ${m.other_user_email_display || 'Email not available'}
                    </div>
                    
                    <div style="text-align: center;">
                        <button class="btn btn-danger" onclick="removeMatch('${m.other_user_id}')" style="margin-top: 10px;">Remove Match</button>
                    </div>
                </div>
            `;
            }).join('');
        }

        // Check if user has any confirmed matches
        const hasConfirmedMatch = confirmed.length > 0;
        
        // Potential Matches Section (people you could swap with)
        // Only show potential matches if user has no confirmed matches
        const potentialMatches = hasConfirmedMatches ? [] : matches.filter(m => !m.i_expressed_interest && !m.mutually_confirmed);
        
        // Pending Requests Section
        const outgoingPending = matches.filter(m => m.i_expressed_interest && !m.mutually_confirmed);
        const incomingPending = matches.filter(m => m.they_expressed_interest && !m.mutually_confirmed);

        const noPending = document.getElementById('noPending');
        const outgoingWrap = document.getElementById('outgoingPending');
        const incomingWrap = document.getElementById('incomingPending');
        const outgoingList = document.getElementById('outgoingPendingList');
        const incomingList = document.getElementById('incomingPendingList');

        // Display potential matches
        const noPotential = document.getElementById('noPotential');
        const potentialList = document.getElementById('potentialList');
        
        if (hasConfirmedMatches) {
            noPotential.style.display = 'block';
            noPotential.innerHTML = '<p>You have a confirmed match! You cannot express interest in other swaps.</p>';
            potentialList.style.display = 'none';
            potentialList.innerHTML = '';
        } else if (potentialMatches.length === 0) {
            noPotential.style.display = 'block';
            noPotential.innerHTML = '<p>No potential matches found. Update your preferences to see more options.</p>';
            potentialList.style.display = 'none';
            potentialList.innerHTML = '';
        } else {
            noPotential.style.display = 'none';
            potentialList.style.display = 'grid';
            
            potentialList.innerHTML = potentialMatches.map(m => {
                const myBadge = getMyPreferenceBadge(m.my_preference_level);
                
                return `
                <div class="listing-card">
                    <div class="listing-header">
                        <div class="listing-title">${m.other_user_name}</div>
                        <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                            ${myBadge}
                            <span style="background: rgba(33, 150, 243, 0.3); padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">Potential Match</span>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 15px; padding: 10px; background: rgba(255, 255, 255, 0.1); border-radius: 8px;">
                        <div style="margin-bottom: 8px;"><strong>Match Details:</strong></div>
                        <div style="font-size: 0.9rem;">
                           ${m.other_current_apartment} (your ${getPreferenceText(m.my_preference_level)} choice)
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 10px;">
                        <button class="btn" onclick="expressInterest('${m.other_user_id}')">Express Interest</button>
                    </div>
                </div>
            `;
            }).join('');
        }

        const hasPending = outgoingPending.length > 0 || incomingPending.length > 0;
        noPending.style.display = hasPending ? 'none' : 'block';

        if (outgoingPending.length > 0) {
            outgoingWrap.style.display = 'block';
            outgoingList.innerHTML = outgoingPending.map(m => `
                <div class="listing-card">
                    <div class="listing-header">
                        <div class="listing-title">${m.other_user_name}</div>
                        <span style="background: rgba(255, 193, 7, 0.3); padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">Waiting</span>
                    </div>
                    <div style="font-size: 0.9rem; margin-bottom: 10px;">
                        You requested to swap with them. They haven't confirmed yet.
                    </div>
                    <div style="margin-bottom: 8px;">
                         ${m.other_current_apartment} (${getPreferenceText(m.my_preference_level)} choice)
                    </div>
                    <div style="text-align: center; margin-top: 10px;">
                        <button class="btn btn-secondary" onclick="withdrawInterest('${m.other_user_id}')">Withdraw Interest</button>
                    </div>
                </div>
            `).join('');
        } else {
            outgoingWrap.style.display = 'none';
            outgoingList.innerHTML = '';
        }

        if (incomingPending.length > 0) {
            incomingWrap.style.display = 'block';
            incomingList.innerHTML = incomingPending.map(m => `
                <div class="listing-card">
                    <div class="listing-header">
                        <div class="listing-title">${m.other_user_name}</div>
                        <span style="background: rgba(33, 150, 243, 0.3); padding: 5px 10px; border-radius: 15px; font-size: 0.8rem;">Interested in You</span>
                    </div>
                    <div style="font-size: 0.9rem; margin-bottom: 10px;">
                        They requested to swap with you. You can accept or decline.
                    </div>
                    <div style="margin-bottom: 8px;">
                        <strong>You want:</strong> ${m.other_current_apartment} (${getPreferenceText(m.my_preference_level)} choice)
                    </div>
                    <div style="text-align: center; margin-top: 10px;">
                        <button class="btn" onclick="acceptInterest('${m.other_user_id}')" style="margin-right: 10px;">Accept Interest</button>
                        <button class="btn btn-secondary" onclick="withdrawInterest('${m.other_user_id}')">Decline</button>
                    </div>
                </div>
            `).join('');
        } else {
            incomingWrap.style.display = 'none';
            incomingList.innerHTML = '';
        }
    } catch (error) {
        console.error('Error loading matches:', error);
    }
}

function showCreateForm() {
    if (hasConfirmedMatches) {
        showAlert('You cannot create a new request while you have a confirmed match.', 'error');
        return;
    }
    
    isEditMode = false;
    document.getElementById('formTitle').textContent = 'Create Swap Request';
    document.getElementById('submitBtn').textContent = 'Create Request';
    document.getElementById('swapForm').reset();
    positionFormInline();
    const formEl = document.getElementById('createEditForm');
    formEl.style.display = 'block';
    formEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showEditForm() {
    if (hasConfirmedMatches) {
        showAlert('You cannot edit your request while you have a confirmed match.', 'error');
        return;
    }
    
    isEditMode = true;
    document.getElementById('formTitle').textContent = 'Edit Swap Request';
    document.getElementById('submitBtn').textContent = 'Update Request';

    // Prefill form from last loaded user request
    if (lastUserRequest) {
        document.getElementById('currentApartment').value = lastUserRequest.current_apartment || '';
        document.getElementById('currentRoom').value = lastUserRequest.current_room || '';
        document.getElementById('firstChoice').value = lastUserRequest.preferences?.first_choice || '';
        document.getElementById('secondChoice').value = lastUserRequest.preferences?.second_choice || '';
        document.getElementById('thirdChoice').value = lastUserRequest.preferences?.third_choice || '';
    }

    positionFormInline();
    const formEl = document.getElementById('createEditForm');
    formEl.style.display = 'block';
    formEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideForm() {
    document.getElementById('createEditForm').style.display = 'none';
}

async function deleteRequest() {
    if (hasConfirmedMatches) {
        showAlert('You cannot delete your request while you have a confirmed match.', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to delete your swap request?')) {
        return;
    }
    
    try {
        const response = await fetch(`/delete-requests/${currentRequestId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Request deleted successfully!', 'success');
            currentRequestId = null;
            lastUserRequest = null;
            loadUserRequest();
            loadMatches();
        } else {
            const data = await response.json();
            showAlert(data.error || 'Error deleting request', 'error');
        }
    } catch (error) {
        showAlert('Error deleting request', 'error');
    }
}

document.getElementById('swapForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Check if user already has a confirmed match
    if (hasConfirmedMatches) {
        showAlert('You cannot create a new request while you have a confirmed match.', 'error');
        return;
    }
    
    const formData = new FormData(e.target);
    const requestData = {
        current_apartment: formData.get('currentApartment'),
        current_room: formData.get('currentRoom'),
        first_choice: formData.get('firstChoice'),
        second_choice: formData.get('secondChoice'),
        third_choice: formData.get('thirdChoice')
    };
    
    try {
        const url = isEditMode ? `/create-requests/${currentRequestId}` : '/create-request';
        const method = isEditMode ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            hideForm();
            loadUserRequest();
            loadMatches();
        } else {
            showAlert(data.error || 'Error saving request', 'error');
        }
    } catch (error) {
        showAlert('Error saving request', 'error');
    }
});

async function expressInterest(otherUserId) {
    if (hasConfirmedMatches) {
        showAlert('You cannot express interest in other swaps while you have a confirmed match.', 'error');
        return;
    }
    
    try {
        const response = await fetch('/express-interest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ other_user_id: otherUserId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            await loadMatches(); // Refresh matches
            // Scroll to Pending section to show the newly added pending card
            const pendingSection = document.getElementById('pendingSection');
            if (pendingSection) {
                pendingSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } else {
            showAlert(data.error || 'Error expressing interest', 'error');
        }
    } catch (error) {
        showAlert('Error expressing interest', 'error');
    }
}

async function withdrawInterest(otherUserId) {
    if (hasConfirmedMatches) {
        showAlert('You cannot withdraw interest while you have a confirmed match.', 'error');
        return;
    }
    
    if (!confirm('Are you sure you want to withdraw your interest in this swap?')) {
        return;
    }
    
    try {
        const response = await fetch('/withdraw-interest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ other_user_id: otherUserId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadMatches(); // Refresh matches
        } else {
            showAlert(data.error || 'Error withdrawing interest', 'error');
        }
    } catch (error) {
        showAlert('Error withdrawing interest', 'error');
    }
}

async function acceptInterest(otherUserId) {
    if (!confirm('Are you sure you want to accept this interest request? This will create a confirmed match and reveal contact information.')) {
        return;
    }
    
    try {
        const response = await fetch('/accept-interest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ other_user_id: otherUserId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadMatches(); // Refresh matches
        } else {
            showAlert(data.error || 'Error accepting interest', 'error');
        }
    } catch (error) {
        showAlert('Error accepting interest', 'error');
    }
}

async function removeMatch(otherUserId) {
    if (!confirm('Are you sure you want to remove this confirmed match? This will break the connection and hide contact information.')) {
        return;
    }
    
    try {
        const response = await fetch('/remove-match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ other_user_id: otherUserId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(data.message, 'success');
            loadMatches(); // Refresh matches
        } else {
            showAlert(data.error || 'Error removing match', 'error');
        }
    } catch (error) {
        showAlert('Error removing match', 'error');
    }
} 