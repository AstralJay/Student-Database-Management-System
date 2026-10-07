document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu = document.querySelector(".nav-menu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            const isOpen = navMenu.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    document.querySelectorAll("[data-toast]").forEach((toast, index) => {
        const dismiss = () => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-8px)";
            window.setTimeout(() => toast.remove(), 180);
        };

        const closeButton = toast.querySelector("[data-toast-close]");
        if (closeButton) {
            closeButton.addEventListener("click", dismiss);
        }

        window.setTimeout(dismiss, 4500 + (index * 400));
    });

    const searchInput = document.querySelector("[data-record-search]");
    const gradeFilter = document.querySelector("[data-record-filter]");
    const sortSelect = document.querySelector("[data-record-sort]");
    const rows = Array.from(document.querySelectorAll("[data-record-row]"));

    const renderRows = () => {
        if (!rows.length) {
            return;
        }

        const query = (searchInput?.value || "").trim().toLowerCase();
        const grade = gradeFilter?.value || "";
        const sortBy = sortSelect?.value || "recent";

        rows.forEach((row) => {
            const haystack = (row.dataset.search || "").toLowerCase();
            const rowGrade = row.dataset.grade || "";
            const matchesQuery = !query || haystack.includes(query);
            const matchesGrade = !grade || rowGrade === grade;
            row.classList.toggle("hidden", !(matchesQuery && matchesGrade));
        });

        const visibleRows = rows.filter((row) => !row.classList.contains("hidden"));
        const tbody = visibleRows[0]?.parentElement;
        if (!tbody) {
            return;
        }

        visibleRows
            .sort((a, b) => {
                if (sortBy === "marks") {
                    return Number(b.dataset.marks || 0) - Number(a.dataset.marks || 0);
                }
                if (sortBy === "attendance") {
                    return Number(b.dataset.attendance || 0) - Number(a.dataset.attendance || 0);
                }
                if (sortBy === "course") {
                    return (a.dataset.course || "").localeCompare(b.dataset.course || "");
                }
                return Number(b.dataset.index || 0) - Number(a.dataset.index || 0);
            })
            .forEach((row) => tbody.appendChild(row));
    };

    [searchInput, gradeFilter, sortSelect].forEach((control) => {
        if (control) {
            control.addEventListener("input", renderRows);
            control.addEventListener("change", renderRows);
        }
    });
    renderRows();

    const chainSearch = document.querySelector("[data-chain-search]");
    const blockCards = Array.from(document.querySelectorAll("[data-block-card]"));

    if (chainSearch && blockCards.length) {
        chainSearch.addEventListener("input", () => {
            const query = chainSearch.value.trim().toLowerCase();
            blockCards.forEach((card) => {
                const haystack = (card.dataset.search || "").toLowerCase();
                card.classList.toggle("hidden", Boolean(query) && !haystack.includes(query));
            });
        });
    }

    const verifyButton = document.querySelector("[data-verify-chain]");
    const verificationStatus = document.querySelector("[data-verify-status]");
    const verificationMessage = document.querySelector("[data-verify-message]");
    const verificationItems = Array.from(document.querySelectorAll("[data-verify-item]"));
    const recordStatusBadges = Array.from(document.querySelectorAll("[data-record-status]"));
    const verifyStatusInline = document.querySelector("[data-verify-status-inline]");

    const applyVerificationState = (valid, message) => {
        if (verificationStatus) {
            verificationStatus.className = `status-pill ${valid ? "ok" : "bad"}`;
            verificationStatus.innerHTML = valid
                ? '<i class="fa-solid fa-circle-check"></i> Blockchain Verified'
                : '<i class="fa-solid fa-triangle-exclamation"></i> Integrity Check Required';
        }

        if (verificationMessage) {
            verificationMessage.textContent = message;
        }

        verificationItems.forEach((item) => {
            item.classList.remove("status-ok", "status-bad", "status-pending");
            item.classList.add(valid ? "status-ok" : "status-bad");
            item.textContent = valid ? "Valid" : "Review";
        });

        recordStatusBadges.forEach((badge) => {
            badge.classList.remove("status-pending", "status-ok", "status-bad");
            badge.classList.add(valid ? "status-ok" : "status-bad");
            badge.textContent = valid ? "Verified" : "Invalid";
        });

        if (verifyStatusInline) {
            verifyStatusInline.textContent = valid ? "Verified" : "Review";
        }
    };

    const runVerification = async () => {
        if (verifyButton) {
            verifyButton.disabled = true;
            verifyButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying';
        }

        try {
            const response = await fetch("/api/verify", { headers: { "X-Requested-With": "fetch" } });
            const payload = await response.json();
            applyVerificationState(Boolean(payload.valid), payload.message || "Verification completed.");
        } catch (error) {
            applyVerificationState(false, "Unable to verify the blockchain right now.");
        } finally {
            if (verifyButton) {
                verifyButton.disabled = false;
                verifyButton.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Verify Blockchain';
            }
        }
    };

    if (verifyButton) {
        verifyButton.addEventListener("click", runVerification);
    }

    if (verifyButton || recordStatusBadges.length || verifyStatusInline) {
        runVerification();
    }
});
