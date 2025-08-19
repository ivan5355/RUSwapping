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
        // Treat all returned matches as confirmed now
        const confirmed = matches;
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
            editRequestBtn.disabled = false;
            editRequestBtn.textContent = 'Edit Request';
            editRequestBtn.style.opacity = '1';
            editRequestBtn.style.cursor = 'pointer';
        }
        
        if (deleteRequestBtn) {
            deleteRequestBtn.disabled = false;
            deleteRequestBtn.textContent = 'Delete Request';
            deleteRequestBtn.style.opacity = '1';
            deleteRequestBtn.style.cursor = 'pointer';
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
                const myBadge = m.my_preference_level ? getMyPreferenceBadge(m.my_preference_level) : '';
                const preferenceSuffix = m.my_preference_level ? ` (your ${getPreferenceText(m.my_preference_level)} choice)` : '';
                
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
                            • ${m.other_current_apartment}${preferenceSuffix}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 10px;">
                        <strong>They're currently at:</strong> ${m.other_current_apartment || ''}
                        ${m.other_current_room ? ` (${m.other_current_room})` : ''}
                    </div>
                    <div class="contact-info" style="margin-bottom: 15px;">
                        <strong>Contact:</strong> ${m.other_user_email_display || 'Email not available'}
                    </div>
                </div>
            `;
            }).join('');
        }

        // Hide Potential and Pending sections (feature removed)
        const noPotential = document.getElementById('noPotential');
        const potentialList = document.getElementById('potentialList');
        const potentialSection = document.getElementById('potentialSection');
        if (noPotential) noPotential.style.display = 'none';
        if (potentialList) { potentialList.style.display = 'none'; potentialList.innerHTML = ''; }
        if (potentialSection) potentialSection.style.display = 'none';

        const noPending = document.getElementById('noPending');
        const outgoingWrap = document.getElementById('outgoingPending');
        const incomingWrap = document.getElementById('incomingPending');
        const outgoingList = document.getElementById('outgoingPendingList');
        const incomingList = document.getElementById('incomingPendingList');
        if (noPending) noPending.style.display = 'none';
        if (outgoingWrap) outgoingWrap.style.display = 'none';
        if (incomingWrap) incomingWrap.style.display = 'none';
        if (outgoingList) outgoingList.innerHTML = '';
        if (incomingList) incomingList.innerHTML = '';
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
        const url = isEditMode ? '/update-request' : '/create-request';
        const method = 'POST';
        
        const payload = isEditMode ? { ...requestData, request_id: currentRequestId } : requestData;

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
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

