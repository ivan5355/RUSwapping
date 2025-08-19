// Cycle state
let isCycleEditMode = false;
let currentCycleRequestId = null;
let lastCycleUserRequest = null;

// Load data when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadCycleUserRequest();
});

async function loadUserInfo() {
    try {
        const response = await fetch('/get-user-info');
        if (response.ok) {
            const userData = await response.json();
            const userDisplayName = document.getElementById('userDisplayName');
            if (userDisplayName) {
                const fullName = userData.name || 'User';
                userDisplayName.textContent = fullName;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

async function loadCycleUserRequest() {
    try {
        const response = await fetch('/get-cycle-requests');
        const requests = await response.json();
        const userRequest = Array.isArray(requests) ? requests.find(req => req.is_own) : null;
        if (userRequest) {
            lastCycleUserRequest = userRequest;
            currentCycleRequestId = userRequest.id;
            displayCycleUserRequest(userRequest);
            document.getElementById('cycleNoRequest').style.display = 'none';
            document.getElementById('cycleHasRequest').style.display = 'block';
        } else {
            lastCycleUserRequest = null;
            document.getElementById('cycleNoRequest').style.display = 'block';
            document.getElementById('cycleHasRequest').style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading cycle user request:', error);
    }
}

function showCycleCreateForm() {
    isCycleEditMode = false;
    document.getElementById('cycleFormTitle').textContent = 'Create Cycle Swap Request';
    document.getElementById('cycleSubmitBtn').textContent = 'Create Cycle Swap Request';
    document.getElementById('cycleForm').reset();
    positionCycleFormInline();
    const formEl = document.getElementById('cycleCreateEditForm');
    formEl.style.display = 'block';
    formEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showCycleEditForm() {
    isCycleEditMode = true;
    document.getElementById('cycleFormTitle').textContent = 'Edit Cycle Swap Request';
    document.getElementById('cycleSubmitBtn').textContent = 'Update Cycle Swap Request';

    if (lastCycleUserRequest) {
        document.getElementById('cycleCurrentApartment').value = lastCycleUserRequest.current_apartment || '';
        document.getElementById('cycleCurrentRoom').value = lastCycleUserRequest.current_room || '';
        document.getElementById('desiredChoice').value = lastCycleUserRequest.desired_choice || '';
    }

    positionCycleFormInline();
    const formEl = document.getElementById('cycleCreateEditForm');
    formEl.style.display = 'block';
    formEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideCycleForm() {
    document.getElementById('cycleCreateEditForm').style.display = 'none';
}

async function deleteCycleRequest() {
    if (!confirm('Are you sure you want to delete your cycle swap request?')) {
        return;
    }
    try {
        const response = await fetch(`/delete-cycle-requests/${currentCycleRequestId}`, { method: 'DELETE' });
        if (response.ok) {
            showAlert('Cycle swap request deleted successfully!', 'success');
            currentCycleRequestId = null;
            lastCycleUserRequest = null;
            loadCycleUserRequest();
        } else {
            const data = await response.json();
            showAlert(data.error || 'Error deleting cycle swap request', 'error');
        }
    } catch (error) {
        showAlert('Error deleting cycle swap request', 'error');
    }
}

document.getElementById('cycleForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const requestData = {
        current_apartment: formData.get('cycleCurrentApartment'),
        current_room: formData.get('cycleCurrentRoom'),
        desired_choice: formData.get('desiredChoice')
    };
    try {
        const url = isCycleEditMode ? '/update-cycle-request' : '/create-cycle-request';
        const payload = isCycleEditMode ? { ...requestData, request_id: currentCycleRequestId } : requestData;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (response.ok) {
            showAlert(data.message, 'success');
            hideCycleForm();
            loadCycleUserRequest();
        } else {
            showAlert(data.error || 'Error saving cycle swap request', 'error');
        }
    } catch (error) {
        showAlert('Error saving cycle swap request', 'error');
    }
}); 