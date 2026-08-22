// ================= SEARCH SERVICE =================

function searchService() {

    const searchInput =
        document.getElementById("serviceSearch");

    const searchValue =
        searchInput.value.trim();

    if (searchValue === "") {

        alert("कृपया सरकारी सेवा का नाम दर्ज करें.");

        searchInput.focus();

        return;
    }

    alert(
        "Searching for Government Service:\n\n" +
        searchValue
    );
}


// ================= APPLY SERVICE =================

function applyService(serviceName) {

    const confirmation =
        confirm(
            "आप " +
            serviceName +
            " के लिए आवेदन करना चाहते हैं?\n\n" +
            "Continue?"
        );

    if (confirmation) {

        alert(
            serviceName +
            " application page will open here."
        );

        // Later:
        // window.location.href =
        // "application.html?service=" +
        // encodeURIComponent(serviceName);
    }
}


// ================= VIEW ALL SERVICES =================

function viewAllServices() {

    alert(
        "All Government Services page will open here."
    );

    // Later:
    // window.location.href = "services.html";
}


// ================= LOGIN =================

document
    .querySelector(".login-btn")
    .addEventListener("click", function () {

        alert(
            "Login page will open here."
        );

    });


// ================= REGISTER =================

document
    .querySelector(".register-btn")
    .addEventListener("click", function () {

        alert(
            "Registration page will open here."
        );

    });


// ================= SEARCH USING ENTER =================

document
    .getElementById("serviceSearch")
    .addEventListener("keypress", function(event) {

        if (event.key === "Enter") {

            searchService();

        }

    });
const translations = {

    en: {
        home: "Home",
        services: "Services",
        track: "Track Application",
        complaints: "Complaints",
        about: "About Us",
        contact: "Contact Us",

        heroTitle: "All Government Services",
        heroHighlight: "Now on One Portal",

        heroDescription:
            "Apply for government services, track your applications and raise complaints easily, anywhere, anytime.",

        searchPlaceholder:
            "Search Government Services...",

        search: "Search",

        popularServices:
            "Popular Services",

        income:
            "Income Certificate",

        caste:
            "Caste Certificate",

        domicile:
            "Domicile Certificate",

        birth:
            "Birth Certificate",

        seven:
            "7/12 Extract"
    },


    mr: {
        home: "मुख्यपृष्ठ",
        services: "शासकीय सेवा",
        track: "अर्जाचा मागोवा",
        complaints: "तक्रारी",
        about: "आमच्याबद्दल",
        contact: "संपर्क",

        heroTitle:
            "सर्व शासकीय सेवा",

        heroHighlight:
            "आता एकाच पोर्टलवर",

        heroDescription:
            "शासकीय सेवांसाठी अर्ज करा, आपल्या अर्जाची स्थिती तपासा आणि तक्रार नोंदवा – सहज, कुठेही, कधीही.",

        searchPlaceholder:
            "शासकीय सेवा शोधा...",

        search:
            "शोधा",

        popularServices:
            "लोकप्रिय सेवा",

        income:
            "उत्पन्न प्रमाणपत्र",

        caste:
            "जात प्रमाणपत्र",

        domicile:
            "रहिवासी प्रमाणपत्र",

        birth:
            "जन्म प्रमाणपत्र",

        seven:
            "७/१२ उतारा"
    },


    hi: {
        home: "होम",
        services: "सरकारी सेवाएं",
        track: "आवेदन ट्रैक करें",
        complaints: "शिकायतें",
        about: "हमारे बारे में",
        contact: "संपर्क करें",

        heroTitle:
            "सभी सरकारी सेवाएं",

        heroHighlight:
            "अब एक ही पोर्टल पर",

        heroDescription:
            "सरकारी सेवाओं के लिए आवेदन करें, अपनी आवेदन स्थिति ट्रैक करें और आसानी से शिकायत दर्ज करें।",

        searchPlaceholder:
            "सरकारी सेवाएं खोजें...",

        search:
            "खोजें",

        popularServices:
            "लोकप्रिय सेवाएं",

        income:
            "आय प्रमाणपत्र",

        caste:
            "जाति प्रमाणपत्र",

        domicile:
            "निवास प्रमाणपत्र",

        birth:
            "जन्म प्रमाणपत्र",

        seven:
            "7/12 उतारा"
    }
};


const languageSelect =
    document.getElementById("languageSelect");


function changeLanguage(language) {

    const selectedLanguage =
        translations[language];


    // Change text

    document
        .querySelectorAll("[data-key]")
        .forEach(function(element) {

            const key =
                element.getAttribute("data-key");

            if (selectedLanguage[key]) {

                element.innerText =
                    selectedLanguage[key];

            }

        });


    // Change input placeholder

    document
        .querySelectorAll("[data-placeholder]")
        .forEach(function(element) {

            const key =
                element.getAttribute("data-placeholder");

            if (selectedLanguage[key]) {

                element.placeholder =
                    selectedLanguage[key];

            }

        });


    // Save language

    localStorage.setItem(
        "language",
        language
    );
}


// Language change

languageSelect.addEventListener(
    "change",
    function() {

        changeLanguage(this.value);

    }
);


// Load saved language

const savedLanguage =
    localStorage.getItem("language");

if (savedLanguage) {

    languageSelect.value =
        savedLanguage;

    changeLanguage(savedLanguage);

}