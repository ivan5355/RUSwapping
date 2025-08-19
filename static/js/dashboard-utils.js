function positionFormInline() {
    const formSection = document.getElementById('createEditForm');
    const userSection = document.getElementById('userRequestSection');
    if (!formSection || !userSection) return;
    const parentFormSection = userSection.closest('.form-section');
    if (parentFormSection && formSection.previousElementSibling !== parentFormSection) {
        parentFormSection.insertAdjacentElement('afterend', formSection);
    }
}

function getMyPreferenceBadge(myLevel) {
    return `<span style="background: rgba(204,0,51,0.35); padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold;">Your ${getPreferenceText(myLevel)} choice</span>`;
}

function displayUserRequest(request) {
    const card = document.getElementById('userRequestCard');
    card.innerHTML = `
        <div class="listing-header">
            <div class="listing-title">Your Request</div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Currently at:</strong> ${request.current_apartment}
            ${request.current_room ? ` (${request.current_room})` : ''}
        </div>
        
        <div class="swap-arrow">WANTS TO SWAP TO</div>
        
        ${request.preferences?.first_choice ? `<div style=\"margin-bottom: 10px;\"><strong>1st Choice:</strong> ${request.preferences.first_choice}</div>` : ''}
        ${request.preferences?.second_choice ? `<div style=\"margin-bottom: 10px;\"><strong>2nd Choice:</strong> ${request.preferences.second_choice}</div>` : ''}
        ${request.preferences?.third_choice ? `<div style=\"margin-bottom: 10px;\"><strong>3rd Choice:</strong> ${request.preferences.third_choice}</div>` : ''}
        
        <div class="contact-info">
            <small>Posted: ${request.created_at || ''}</small>
        </div>
    `;
}



function getPreferenceText(level) {
    switch(level) {
        case 1: return '1st';
        case 2: return '2nd';
        case 3: return '3rd';
        default: return '';
    }
}

// ---- Cycle helpers ----
function positionCycleFormInline() {
    const formSection = document.getElementById('cycleCreateEditForm');
    const cycleSection = document.getElementById('cycleUserRequestSection');
    if (!formSection || !cycleSection) return;
    const parentFormSection = cycleSection.closest('.form-section');
    if (parentFormSection && formSection.previousElementSibling !== parentFormSection) {
        parentFormSection.insertAdjacentElement('afterend', formSection);
    }
}

function displayCycleUserRequest(request) {
    const card = document.getElementById('cycleUserRequestCard');
    card.innerHTML = `
        <div class="listing-header">
            <div class="listing-title">Your Cycle Request</div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Currently at:</strong> ${request.current_apartment}
            ${request.current_room ? ` (${request.current_room})` : ''}
        </div>
        
        <div class="swap-arrow">WANTS TO SWAP TO</div>
        
        ${request.desired_choice ? `<div style=\"margin-bottom: 10px;\"><strong>Desired:</strong> ${request.desired_choice}</div>` : ''}
        
        <div class="contact-info">
            <small>Posted: ${request.created_at || ''}</small>
        </div>
    `;
} 