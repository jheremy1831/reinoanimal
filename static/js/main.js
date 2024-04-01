const btnDelete = document.querySelectorAll('.btn-delete');
if (btnDelete) {
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if(!confirm("Vas a Eliminar una mascota ¿Estás Seguro?")){
                e.preventDefault();
            }
        });
    })
}