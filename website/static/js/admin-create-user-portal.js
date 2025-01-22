const createUserPortalShowBtn = document.getElementById('createUserPortalShowBtn')
const createUserPortalCloseBtn = document.getElementById('createUserPortalCloseBtn')
const createUserPortal = document.getElementById('createUserPortal')

createUserPortalShowBtn.addEventListener('click', () => {
    createUserPortal.classList.add('open');
});

createUserPortalCloseBtn.addEventListener('click', () => {
    createUserPortal.classList.remove('open');
});