(function() {
  let fieldInFocus = false;

  const toggleMenu = e => {
    let element = document.getElementById("menu-button");
    if (!element || fieldInFocus) return;

    if (element.checked) {
      element.checked = false;
      Array.prototype.forEach.call(
        document.getElementsByClassName("menu-link"),
        el => {
          el.classList.remove("tooltip");
        }
      );
    } else {
      element.checked = true;
      Array.prototype.forEach.call(
        document.getElementsByClassName("menu-link"),
        el => {
          el.classList.add("tooltip");
        }
      );
    }
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
    if (o) {
      return element.classList.remove("is-active");
    }
    element.classList.toggle("is-active");
  };

  const keysHandler = () => {
    document.onkeydown = e => {
      switch (e.key) {
        case ".":
          toggleMenu(e);
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
    document.getElementById("help-close").addEventListener("click", e => {
      toggleHelp(e, true);
    });

    Array.prototype.forEach.call(document.getElementsByTagName("input"), el => {
      el.addEventListener("focus", () => {
        fieldInFocus = true;
      });
      el.addEventListener("blur", () => {
        fieldInFocus = false;
      });
    });
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
