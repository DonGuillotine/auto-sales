(function ($) {
    "use strict";

    /*****************************
    * Commons Variables
    *****************************/
    var $window = $(window),
    $body = $('body');

    /****************************
    * Sticky Menu
    *****************************/
    $(window).on('scroll',function() {
        var scroll = $(window).scrollTop();
        if (scroll < 100) {
         $(".sticky-header").removeClass("sticky");
        }else{
         $(".sticky-header").addClass("sticky");
        }
    });


    /*****************************
    * Off Canvas Function
    *****************************/
    (function () {
        var $offCanvasToggle = $('.offcanvas-toggle'),
            $offCanvas = $('.offcanvas'),
            $offCanvasOverlay = $('.offcanvas-overlay'),
            $mobileMenuToggle = $('.mobile-menu-toggle');
            $offCanvasToggle.on('click', function (e) {
                e.preventDefault();
                var $this = $(this),
                    $target = $this.attr('href');
                $body.addClass('offcanvas-open');
                $($target).addClass('offcanvas-open');
                $offCanvasOverlay.fadeIn();
                if ($this.parent().hasClass('mobile-menu-toggle')) {
                    $this.addClass('close');
                }
            });
            $('.offcanvas-close, .offcanvas-overlay').on('click', function (e) {
                e.preventDefault();
                $body.removeClass('offcanvas-open');
                $offCanvas.removeClass('offcanvas-open');
                $offCanvasOverlay.fadeOut();
                $mobileMenuToggle.find('a').removeClass('close');
            });
    })();


    /**************************
     * Offcanvas: Menu Content
     **************************/
    function mobileOffCanvasMenu() {
        var $offCanvasNav = $('.offcanvas-menu'),
            $offCanvasNavSubMenu = $offCanvasNav.find('.mobile-sub-menu');

        /*Add Toggle Button With Off Canvas Sub Menu*/
        $offCanvasNavSubMenu.parent().prepend('<div class="offcanvas-menu-expand"></div>');

        /*Category Sub Menu Toggle*/
        $offCanvasNav.on('click', 'li a, .offcanvas-menu-expand', function (e) {
            var $this = $(this);
            if ($this.attr('href') === '#' || $this.hasClass('offcanvas-menu-expand')) {
                e.preventDefault();
                if ($this.siblings('ul:visible').length) {
                    $this.parent('li').removeClass('active');
                    $this.siblings('ul').slideUp();
                    $this.parent('li').find('li').removeClass('active');
                    $this.parent('li').find('ul:visible').slideUp();
                } else {
                    $this.parent('li').addClass('active');
                    $this.closest('li').siblings('li').removeClass('active').find('li').removeClass('active');
                    $this.closest('li').siblings('li').find('ul:visible').slideUp();
                    $this.siblings('ul').slideDown();
                }
            }
        });
    }
    mobileOffCanvasMenu();


    /******************************
     * Hero Slider - [Single Grid]
     *****************************/
    $('.hero-area-wrapper').slick({
        arrows: false,
        fade: true,
        dots: true,
        easing: 'linear',
        speed: 2000,
    });

    /************************************************
     * Product Slider - Style: Default [4 Grid, 1 Row]
     ***********************************************/
    $('.product-default-slider-4grids-1row').slick({
        arrows: true,
        infinite: false,
        slidesToShow: 4,
        slidesToScroll: 1,
        rows: 1,
        easing: 'ease-out',
        speed: 1000,
        prevArrow: '<button type="button" class="default-slider-arrow default-slider-arrow--left prevArrow"><i class="fa fa-angle-left"></button>',
        nextArrow: '<button type="button"  class="default-slider-arrow default-slider-arrow--right nextArrow"><i class="fa fa-angle-right"></button>',
        responsive: [

            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2,
                }
            },
            {
                breakpoint: 575,
                settings: {
                    slidesToShow: 1,
                }
            },
        ]
    });

    /************************************************
     * Company logo Slider
     ***********************************************/
    $('.company-logo-slider').slick({
        autoplay: true,
        infinite:true,
        arrows: false,
        slidesToShow: 4,
        slidesToScroll: 1,
        easing: 'linear',
        speed: 1000,
        responsive: [
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 4
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 2
                }
            }
        ]
    });
    /***********************************
    * Gallery - Horizontal
    ************************************/
   $('.product-large-image-horaizontal').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.product-image-thumb-horizontal'
    });
    $('.product-image-thumb-horizontal').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        focusOnSelect: true,
        arrows: true,
        asNavFor: '.product-large-image-horaizontal',
        prevArrow: '<button type="button" class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-left prevArrow"><i class="fa fa-angle-left"></i></button>',
        nextArrow: '<button type="button"  class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-right nextArrow"><i class="fa fa-angle-right"></i></button>',
        responsive: [
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 2
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 2
                }
            }
        ]
    });
    /***********************************
    * Gallery - Vertical
    ************************************/
   $('.product-large-image-vertical').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.product-image-thumb-vertical'
    });
    $('.product-image-thumb-vertical').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        focusOnSelect: true,
        arrows: true,
        vertical: true,
        asNavFor: '.product-large-image-vertical',
        prevArrow: '<button type="button" class="gallery-nav gallery-nav-vertical gallery-nav-vertical-up prevArrow"><i class="fa fa-angle-up"></i></button>',
        nextArrow: '<button type="button"  class="gallery-nav gallery-nav-vertical gallery-nav-vertical-down nextArrow"><i class="fa fa-angle-down"></i></button>',
        responsive: [
            {
                breakpoint: 1200,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 3
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 3
                }
            }
        ]
    });


    /********************************
    *  Product Gallery - Image Zoom
    **********************************/
    $('.zoom-image-hover').zoom();

    /***********************************
    * Gallery - Single Slider
    ************************************/
    $('.product-large-image-single-slider').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        focusOnSelect: true,
        arrows: true,
        prevArrow: '<button type="button" class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-left prevArrow"><i class="fa fa-angle-left"></i></button>',
        nextArrow: '<button type="button"  class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-right nextArrow"><i class="fa fa-angle-right"></i></button>',
        responsive: [

            {
                breakpoint: 992,
                settings: {
                    slidesToShow: 3,
                }
            },
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 2,
                    arrows: false,
                    autoplay: true,
                    infinite: true,
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    arrows: false,
                    autoplay: true,
                    infinite: true,
                }
            }
        ]
    });

    /***********************************
    * Modal  Quick View Image
    ************************************/
   $('.modal-product-image-large').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: false,
        fade: true,
        asNavFor: '.modal-product-image-thumb'
    });
    $('.modal-product-image-thumb').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        asNavFor: '.modal-product-image-large',
        focusOnSelect: true,
        prevArrow: '<button type="button" class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-left prevArrow"><i class="fa fa-angle-left"></i></button>',
        nextArrow: '<button type="button"  class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-right nextArrow"><i class="fa fa-angle-right"></i></button>',
    });
    $('.modal').on('shown.bs.modal', function (e) {
        $('.modal-product-image-large, .modal-product-image-thumb').slick('setPosition');
        $('.product-details-gallery-area').addClass('open');
    });

    /***********************************
    * Blog - Slider
    ************************************/
   $('.blog-image-slider').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        focusOnSelect: true,
        arrows: true,
        prevArrow: '<button type="button" class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-left prevArrow"><i class="fa fa-angle-left"></i></button>',
        nextArrow: '<button type="button"  class="gallery-nav gallery-nav-horizontal gallery-nav-horizontal-right nextArrow"><i class="fa fa-angle-right"></i></button>',
    });

    /***********************************
    * Testimonial - Slider
    ************************************/
   $('.testimonial-slider').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        focusOnSelect: true,
        dots: true,
        arrows: false,
    });

    /************************************************
     * Nice Select
     ***********************************************/
    $('select').niceSelect();

    /************************************************
     * Price Slider
     ***********************************************/
    $( "#slider-range" ).slider({
        range: true,
        min: 0,
        max: 500,
        values: [ 75, 300 ],
        slide: function( event, ui ) {
          $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
        }
      });
      $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
        " - $" + $( "#slider-range" ).slider( "values", 1 ) );


    /************************************************
     * Video  Popup
     ***********************************************/
    $('.video-play-btn').venobox();

    /************************************************
    * Animate on Scroll
    ***********************************************/
    AOS.init({
        // Settings that can be overridden on per-element basis, by `data-aos-*` attributes:
        duration: 1000, // values from 0 to 3000, with step 50ms
        once: true, // whether animation should happen only once - while scrolling down
        easing: 'ease',
    });
    window.addEventListener('load', AOS.refresh);

    /************************************************
    * Hash Link Scroll To Top Prevent
    ***********************************************/
    $('a[href="#"]').on('click', (function(e) {
    e.preventDefault ? e.preventDefault() : e.returnValue = false;
    }));

    /************************************************
     * Scroll Top
     ***********************************************/
    $('body').materialScrollTop();


})(jQuery);
