(() => {
  let fieldInFocus = false;

  const toggleMenu = (e, o = false) => {
    let element = document.getElementById("menu-button");
    if (!element || fieldInFocus) return;
    if (o === true) element.checked ^= 1;

    if (element.checked) {
      Array.prototype.forEach.call(
        document.getElementsByClassName("menu-link"),
        el => {
          el.classList.remove("tooltip");
        }
      );
    } else {
      Array.prototype.forEach.call(
        document.getElementsByClassName("menu-link"),
        el => {
          el.classList.add("tooltip");
        }
      );
    }
    document.cookie = `menu=${element.checked ? "1" : "0"};path=/`;
  };

  const toggleSearch = e => {
    if (!fieldInFocus) {
      e.preventDefault();
      let element = document.getElementById("search");
      element && element.focus();
    }
  };

  const toggleHelp = (e, o = false) => {
    let element = document.getElementById("help");
    if (!element || fieldInFocus) return;
    e.preventDefault();
    if (o === true) return element.classList.remove("is-active");
    element.classList.toggle("is-active");
  };

  const keysHandler = () => {
    document.onkeydown = e => {
      switch (e.key) {
        case ".":
          toggleMenu(e, true);
          break;
        case "/":
          toggleSearch(e);
          break;
        case "?":
          toggleHelp(e);
          break;
        case "Escape":
          toggleHelp(e, true);
          break;
        default:
      }
    };
  };

  const eventsHandler = () => {
    document.getElementById("menu-button").addEventListener("change", e => {
      toggleMenu(e);
    });

    document.getElementById("help-close").addEventListener("click", e => {
      toggleHelp(e, true);
    });

    Array.prototype.forEach.call(
      document.querySelectorAll("tr.is-clickable"),
      el => {
        el.addEventListener("click", () => {
          window.location = el.getAttribute("href");
        });
        el.addEventListener("mouseover", () => {
          document.status = el.getAttribute("href");
        });
      }
    );

    Array.prototype.forEach.call(
      document.querySelectorAll("input,textarea"),
      el => {
        if (["checkbox", "hidden"].includes(el.type)) return;
        el.addEventListener("focus", () => {
          fieldInFocus = true;
        });
        el.addEventListener("blur", () => {
          fieldInFocus = false;
        });
      }
    );

    Array.prototype.forEach.call(
      document.getElementsByClassName("delete"),
      el => {
        el.addEventListener("click", () => {
          el.parentNode.remove();
        });
      }
    );

    Array.prototype.forEach.call(
      document.getElementsByClassName("notification"),
      (el, i) => {
        setTimeout(() => {
          el.remove();
        }, 5000 + i * 500);
      }
    );
  };

  const initialise = () => {
    keysHandler();
    eventsHandler();
  };
  initialise();
})();
