from playwright.async_api import Page

from .models import BrowserElement, ElementDimensions


class BrowserOperator(object):
    async def detect_interactive_elements(self, page: Page) -> list[BrowserElement]:
        await page.wait_for_load_state("domcontentloaded")
        interactive_elements = await page.evaluate(
            """() => {
            const clickableSelectors = [
                // Standard interactive elements
                'a', 'button', 'input', 'select', 'textarea', 'label',
                'details', 'summary', 'audio[controls]', 'video[controls]',
                
                // Form elements
                'form', 'fieldset', 'legend', 'option', 'optgroup',
                'input[type="text"]', 'input[type="password"]', 'input[type="checkbox"]',
                'input[type="radio"]', 'input[type="submit"]', 'input[type="reset"]',
                'input[type="file"]', 'input[type="image"]', 'input[type="button"]',
                'input[type="search"]', 'input[type="email"]', 'input[type="tel"]',
                'input[type="number"]', 'input[type="range"]', 'input[type="date"]',
                
                // Elements with tabindex
                '[tabindex]:not([tabindex="-1"])',
                
                // ARIA roles for interactive elements
                '[role="button"]', '[role="link"]', '[role="checkbox"]', '[role="radio"]',
                '[role="tab"]', '[role="menuitem"]', '[role="menuitemcheckbox"]', 
                '[role="menuitemradio"]', '[role="option"]', '[role="switch"]',
                '[role="textbox"]', '[role="searchbox"]', '[role="spinbutton"]',
                
                // Elements with event handlers
                '[onclick]', '[onmousedown]', '[onmouseup]', '[ontouchstart]',
                '[ontouchend]', '[onkeydown]', '[onkeyup]',
                
                // Common CSS classes for interactive components
                '.btn', '.button', '.clickable', '.link', '.nav-link', '.dropdown-item',
                '.menu-item', '.nav-item', '.toggle', '.switch', '.accordion-button',
                '.card-link', '.page-link', '.list-group-item', '.icon-button',
                '.close', '.dismiss', '.tab-link',
                
                // Common UI frameworks
                '.dropdown-toggle', '.navbar-toggler', '.page-item', '.carousel-control',
                '.modal-header .close', '.nav-tabs .nav-link',
                
                // Material Design
                '.mdc-button', '.mat-button', '.mat-icon-button', '.mat-menu-item',
                '.mat-tab-label', '.mat-checkbox', '.mat-radio-button',
                
                // Data attributes often used for JS hooks
                '[data-toggle]', '[data-target]', '[data-dismiss]', '[data-close]',
                '[data-open]', '[data-action]', '[data-trigger]', '[data-bs-toggle]',
                '[data-bs-target]', '[data-bs-dismiss]'
            ];
            
            const elements = Array.from(
                document.querySelectorAll(clickableSelectors.join(','))
            );
            
            const visibleElements = elements.filter(el => {
                const style = window.getComputedStyle(el);
                const dimensions = el.getBoundingClientRect();
                return style.display !== 'none' && style.visibility !== 'hidden' && dimensions.width > 0 && dimensions.height > 0;
            });
            
            return visibleElements.slice(0, 200).map(el => {
                const dimensions = el.getBoundingClientRect();
                const result = {
                    text: (el.textContent || '').substring(0, 20),
                    tag_name: el.tagName.toLowerCase(),
                    id: el.id || '',
                    class_name: el.className || '',
                    href: el.href || '',
                    type: el.type || '',
                    placeholder: el.placeholder || '',
                    role: el.getAttribute('role') || '',
                    dimensions: {
                        left: Math.round(dimensions.left),
                        top: Math.round(dimensions.top),
                        width: Math.round(dimensions.width),
                        height: Math.round(dimensions.height)
                    }
                };
                
                return result;
            });
        }"""
        )

        return [BrowserElement(**element) for element in interactive_elements]

    async def visualize_clickable_elements(
        self, page: Page, elements: list[BrowserElement]
    ):
        await page.wait_for_load_state("domcontentloaded")
        await page.evaluate(
            """(elements) => {
            // Remove all previous overlays
            const existingOverlays = document.querySelectorAll('div[style*="border: 2px solid red"]');
            existingOverlays.forEach(overlay => {
                overlay.remove();
            });

            elements.forEach((dimensions, index) => {
                const overlay = document.createElement('div');
                overlay.style.position = 'absolute';
                overlay.style.left = dimensions.left + 'px';
                overlay.style.top = dimensions.top + 'px';
                overlay.style.width = dimensions.width + 'px';
                overlay.style.height = dimensions.height + 'px';
                overlay.style.border = `1px solid red`;
                overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.05)';
                overlay.style.zIndex = '10000';
                overlay.style.pointerEvents = 'none';
                
                const label = document.createElement('span');
                label.style.background = 'black';
                label.style.color = 'white';
                label.style.fontSize = '12px';
                label.style.padding = '2px';
                label.textContent = String(index + 1);
                
                overlay.appendChild(label);
                document.body.appendChild(overlay);
            });
        }""",
            [el.dimensions.model_dump() for el in elements],
        )
