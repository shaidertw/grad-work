function confirmDelete(orgName) {
    Swal.fire({
        title: 'Вы уверены?',
        text: `Хеши ${orgName.split("-")[0]} будут удалены!`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Да, удалить!',
        cancelButtonText: 'Выйти',
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                type: "POST",
                url: "/api/user/delete_hashes/",
                data: { org_name: orgName },
                success: function(data) {
                    console.log(data);
                },
                error: function(error) {
                    console.error(error);
                }
            });
        }
    });
}

function resetSearch() {
  const elementsList = document.getElementById('elementsList');
  const elements = elementsList.getElementsByTagName('li');

  for (let i = 0; i < elements.length; i++) {
    elements[i].style.display = '';
  }
  document.getElementById('searchInput').value = '';
}

function searchElements() {
  const searchText = document.getElementById('searchInput').value.toLowerCase();
  const elementsList = document.getElementById('elementsList');
  const elements = elementsList.getElementsByTagName('li');

  for (let i = 0; i < elements.length; i++) {
    const elementName = elements[i].innerText.toLowerCase();
    if (elementName.includes(searchText)) {
      elements[i].style.display = '';
    } else {
      elements[i].style.display = 'none';
    }
  }
}
