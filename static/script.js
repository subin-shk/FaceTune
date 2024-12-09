<script>
document.addEventListener("DOMContentLoaded", function () {
  const searchBtn = document.getElementById("searchBtn");
  const inputSearch = document.getElementById("inputSearch");
  const searchForm = document.getElementById("searchForm");
  let isInputOpened = false;

  searchBtn.addEventListener("click", function () {
    // If input is not open, open it
    if (!isInputOpened) {
      inputSearch.style.width = "300px"; // Open the input field
      inputSearch.focus();
      isInputOpened = true;
    } else {
      // If input is already open, submit the form
      searchForm.submit();
    }
  });

  inputSearch.addEventListener("blur", function () {
    // If the input is empty, close it when losing focus
    if (inputSearch.value === "") {
      inputSearch.style.width = "50px"; // Collapse the input field back
      isInputOpened = false;
    }
  });

  // Allow reopening the input by clicking the search button again
  inputSearch.addEventListener("focus", function () {
    // Make sure the input is open if it's clicked back into
    if (!isInputOpened) {
      inputSearch.style.width = "300px";
      isInputOpened = true;
    }
  });
});
</script>