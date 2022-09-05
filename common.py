from typing import Tuple

HOME_URL = "https://www.facebook.com/"
BUSINESS_URL = "https://business.facebook.com"
YOUR_PAGES_URL = "https://www.facebook.com/pages/?category=your_pages&ref=bookmarks"
PROFILE_URL = HOME_URL + "me/"


# Todo: maybe move this to the facebook as selectors are useful only there?

class Selector:
    def __init__(self, xpaths: Tuple[str, ...], description: str = ""):
        self.xpaths = xpaths
        self.description = description


# Todo:
# update page class by_xpath with find with selector, get the first non empty list found
# two lists of new_selector and old ui selectors in global settings file
# make use of the selector name/description in logs if any error or not found when needed in the code

# New UI selectors
class SELECTORS:
    fbHome = Selector(('//a[@aria-label="Accueil"]',), "Facebook home icon in top bar")
    fbLogo = Selector(('//a[@aria-label="Facebook"]', '//a[@aria-label="Business Home"]'),
                      "Facebook logo on home page for homing the cursor")
    profileBtn = Selector(
        ('//div[@class="buofh1pr"]//a', '//a[starts-with(@href,"/me/")]',
         '//div[@class="ehxjyohh kr520xx4 poy2od1o b3onmgus hv4rvrfc n7fi1qx3"]//a'),
        "Profile button on the right top bar")

    # profileBtnDiv = Selector(
    #     ('/html/body/div[1]/div/div[1]/div/div[1]/div[1]/div[1]/div[1]',),
    #     "Profile button on the left side bar to click on")

    fName = Selector(
        ('(//div[@data-pagelet="LeftRail"]//a)[1]',
         '(//span[@style="-webkit-box-orient:vertical;-webkit-line-clamp:2;display:-webkit-box"])[1]',
         '//span[text()="See your profile"]/../../div/span'),
        "Get first name of the user from left drawer panel for new ui"
    )
    fName_old = Selector(
        ('(//div[@id="userNav"]//a)[last()]/div',),
        "Get first name of the user from left drawer panel for old ui"
    )
    email = Selector(('//input[@id="email"]',),
                     "Email input on the main login page"
                     )
    passwd = Selector(('//input[@id="pass"]',),
                      "Password input on the main login page"
                      )
    login = Selector(('//button[@type="submit"]',),
                     "Submit buttom on the main login page"
                     )
    woymTB = Selector(('//div[@class="m9osqain a5q79mjw gy2v8mqq jm1wdb64 k4urcfbm qv66sw1b"]',),
                      "What's on your mind text box on profile page"
                      )
    pubBtn = Selector((
        '//div[@role="button" and @aria-label="Publier"]',),
        "Publish post button on profile page"
    )
    closePub = Selector((
        '//div[@class="fcg2cn6m pmk7jnqg cypi58rs"]',),
        "Publish post close button on profile page"
    )

    mediaBtn = Selector(('//div[@aria-label="Ajouter à votre publication"]/../..//i[@class="hu5pjgll bixrwtb6"]',),
                        'Media upload button')
    fileInput = Selector(('//div[@role="dialog"]//input[@type="file" and @class="mkhogb32"]',
                          '//div[@class="dwxx2s2f dicw6rsg kady6ibp rs0gx3tq"]//input[@type="file"]'),
                         "File upload button on new post dialog"
                         )
    fPostSpan = Selector((
        '(//div[@role="article"]//span[@class="tojvnm2t a6sixzi8 abs2jz4q a8s20v7p t1p8iaqh k5wvi7nf q3lfd5jv pk4s997a bipmatt0 cebpdrjk qowsmv63 owwhemhu dp1hu0rb dhp61c6y iyyx5f41"])[1]',),
        "First post link span container on profile page"
    )
    fPostLink = Selector((
        '(//div[@role="article"]//span[@class="tojvnm2t a6sixzi8 abs2jz4q a8s20v7p t1p8iaqh k5wvi7nf q3lfd5jv pk4s997a bipmatt0 cebpdrjk qowsmv63 owwhemhu dp1hu0rb dhp61c6y iyyx5f41"])[1]//a',),
        "First post link on profile page"
    )
    actorSelector = Selector(('(//button[./img[@class="s45kfl79 emlxlaya bkmhp75w spb7xbtv kady6ibp"]])[1]',),
                             "Choose actor dropdown to react to the post"
                             )
    actorList = Selector(('//div[@role="menuitemradio"]',),
                         "Get all actor from the dropdown to react to the post"
                         )
    actorSelect = Selector(('//div[@role="menuitemradio" and .//span[text()="####"]]',),
                           "Choose specific actor from the dropdown to react to the post"
                           )
    reactBtn = Selector(('(//span[@class=" _18vi"])[1]',
                         '//div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t g5gj957u d2edcug0 hpfvmrgz rj1gh0hx buofh1pr n8tt0mok hyh9befq iuny7tx3 ipjc6fyt"]',
						 '//div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t d2edcug0 hpfvmrgz rj1gh0hx buofh1pr g5gj957u n8tt0mok hyh9befq iuny7tx3 ipjc6fyt"]',
                         '//div[@aria-label="J’aime"][1]',),
                        "Reaction button to react to the post"
                        )
    likeBtn = Selector(('//div[@aria-label="J’aime"]',),
                       "Like button to react to the post"
                       )
    loveBtn = Selector(('//div[@aria-label="J’adore"]',),
                       "Love button to react to the post"
                       )
    wowBtn = Selector(('//div[@aria-label="Wouah"]',),
                      "Wow button to react to the post"
                      )
    reactedBtn = Selector(('(//div[@class="e71nayrh  _18vj"])[1]/span[@class="q9uorilb sf5mxxl7"]',
                           '//div[@class="d2edcug0 oh7imozk tr9rh885 abvwweq7 ejjq64ki"]//div[@aria-label="Supprimer J’aime"]'),
                          "Already reacted button check on post page"
                          )
    commentBox = Selector(('(//div[@class="_1mf _1mj"])[1]',
                           '(//div[@aria-label="Écrire un commentaire"])[1]',
                           '(//div[@aria-label="Write a comment"])[1]',
                           ),
                          "Text box to comment on the post page"
                          )
    likedPages = Selector(('//div[@class="rq0escxv rj1gh0hx buofh1pr ni8dbmo4 stjgntxs l9j0dhe7"]//a',),
                          "Liked pages links by user on profile page"
                          )
    pagePubs = Selector(('//div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]',
                         '(//div[@role="feed"])[last()]//div[@class="sjgh65i0 l9j0dhe7 k4urcfbm du4w35lb"]',
                         '//div[@class="sjgh65i0 l9j0dhe7 k4urcfbm du4w35lb"]'),
                        "Page publications"
                        )
    reactTxt = Selector(('.//span[@class="pcp91wgn"]',),
                        "Publication reaction count text"
                        )
    pubLink = Selector((
        './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 m9osqain"]',),
        "Publication link"
    )
    pubShrBtn = Selector(('.//span[text()="Partager"]',),
                         "Publication share button"
                         )
    shrPblc = Selector(('//span[text()="Partager maintenant (Public)"]',),
                       "Publication share public button"
                       )
    shrFrnd = Selector(('//span[text()="Partager maintenant (Amis)"]',),
                       "Publication share public button"
                       )
    #     Moderation script selectors
    apLink = Selector(('//span[text()="Personnes touchées"]',),
                      "Affected persons link on post page"
                      )
    spamCount = Selector(
        ('(//div[@class="n99xedck j83agx80 bp9cbjyn" and .//span[text()="Signaler comme indésirable"]]//span)[1]',),
        "Spam count on post page"
    )

    hide_all_pubs = Selector((
        '(//div[@class="n99xedck j83agx80 bp9cbjyn" and .//span[text()="Masquer toutes les publications"]]//span)[1]',),
        "Hidden posts")

    hide_pub = Selector(
        ('(//div[@class="n99xedck j83agx80 bp9cbjyn" and .//span[text()="Masquer la publication"]]//span)[1]',),
        "Hide post")

    disliked_page = Selector(
        ('(//div[@class="n99xedck j83agx80 bp9cbjyn" and .//span[text()="Je n’aime plus la Page"]]//span)[1]',),
        "Don't Like the post anymore")

    rptCloseBtn = Selector(
        ('//i[@class="hu5pjgll m6k467ps sp_fDmBvoTd0yc sx_4bf4b7"]', '//div[@aria-label="Fermer"]'),
        "Report close button on post page"
    )
    brknPage = Selector(
        ('//h2[contains(text(),"est pas disponible")]',
         '//span[contains(text(),"est pas disponible")]'),
        "Broken page"
    )
    tooManyActions = Selector(
        ('//*[contains(text(),"est temporairement bloqu")]',),
        "Too many actions"
    )
    mainPost = Selector(
        ('//div[@class="d2edcug0 oh7imozk tr9rh885 abvwweq7 ejjq64ki"]/div',),
        "Check that required post is loaded on the page"
    )
    postTitle = Selector(
        ('//h2//span[@class ="nc684nl6"]',
         '//h2',
            '//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p"]',
            '//a[@data-hovercard-prefer-more-content-show="1"][not(@aria-hidden="true")]',
            '//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8"]/strong/span',
            '//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl py34i1dx gpro0wi8"]/span/span'),

        "Published post title"
    )
    postContent = Selector(
        (
            '(//div[@data-ad-preview="message"])[1]',
            '(//div[@class="qt6c0cv9 hv4rvrfc dati1w0a jb3vyjys"])[1]//div[@class="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql"]/..',
            '//div[@data-testid="post_message"]',
            '//div[@data-ad-comet-preview="message"]/div/div/span',),
        "Published post content"
    )
    post_header = Selector(
        ("//img[@data-imgperflogname='profileCoverPhoto']",),
        "Published post header"
    )
    postUnavailable = Selector((
        '//span[@class="oi732d6d ik7dh3pa d2edcug0 qv66sw1b c1et5uql a8c37x1j muag1w35 ew0dbk1b o3w64lxj b2s5l15y hnhda86s m9osqain oqcyycmt"]',),
        "Post unavailable dialog")

    postFrequentReactions = Selector((
        '//h2[@class="oo9gr5id o3w64lxj hnhda86s lzcic4wl oi732d6d ik7dh3pa d2edcug0 qv66sw1b c1et5uql a8c37x1j muag1w35 ew0dbk1b b2s5l15y ni8dbmo4 stjgntxs ltmttdrg g0qnabr5"]',),
        "Too many reactions pop up")
    unhidComment = Selector((
        './/div[text()="Afficher"]',
        './/a[text()="Afficher"]'),
        "Unhide comment")
    invisibleComment = Selector(
        (
            '//div[@class="l9j0dhe7 qwwmc0zo ecm0bbzt rz4wbd8a qt6c0cv9 dati1w0a j83agx80 btwxx1t3 lzcic4wl"]',
            '//div[@aria-label="Commenter" and contains(@class,"aero")]',
            '//div[@aria-label="Réponse au commentaire" and contains(@class,"aero")]',),
        "Invisible comments"
    )
    commentUser = Selector(('.//span[@class="pq6dq46d"]',
                            './/a[@class="_6qw4"]',
                            './/span[@class="gvxzyvdx aeinzg81 t7p7dqev gh25dzvf exr7barw b6ax4al1 gem102v4 ncib64c9 mrvwc6qr sx8pxkcf f597kf1v cpcgwwas f5mw3jnl szxhu1pg nfkogyam kkmhubc1 innypi6y pbevjfx6"]',
                            ),
        "Comment username link")
    visibleCommentCtrl = Selector(('.//div[@class="q9uorilb sf5mxxl7 pgctjfs5"]',
                                   './/i[@class="hu5pjgll m6k467ps sp_fDmBvoTd0yc sx_c66e7f"]/..',
                                   './/button[@tooltip="Supprimer, masquer ou signaler"]',
                                   './/div[@aria-label="Supprimer, masquer ou signaler un abus cela"]',
                                   ),
                                  "Visible comment controls")
    hideComment = Selector(('//span[text()="Masquer le commentaire"]',), "Hide comment")
    visibleComment = Selector(
        ("(//div[@aria-posinset='1'])[1]//div[@class[contains(.,'l9j0dhe7') and contains(.,'ecm0bbzt') and contains(.,'rz4wbd8a') and contains(.,'qt6c0cv9') and contains(.,'dati1w0a') and contains(.,'j83agx80') and contains(.,'btwxx1t3') and contains(.,'lzcic4wl')]]",
         '//div[@class="l9j0dhe7 ecm0bbzt rz4wbd8a qt6c0cv9 dati1w0a j83agx80 btwxx1t3 lzcic4wl"]',
         '//div[@aria-label="Commenter" and not(contains(@class,"aero"))]',
         '(//div[@aria-posinset="1"])[1]//div[contains(@aria-label, "Commentaire de ")]',

         ),
        'Visible comments')
    visibleCommentResponse = Selector(
        ('//div[@class="l9j0dhe7 ecm0bbzt rz4wbd8a qt6c0cv9 scb9dxdr j83agx80 btwxx1t3 lzcic4wl"]',
         '//div[@aria-label="Réponse au commentaire" and not(contains(@class,"aero"))]',
         '//div[contains(@aria-label, "Réponse de ") and (contains(@class,"om3e55n1 d2hqwtrz oxkhqvkx rl78xhln fwlpnqze alzwoclg jl2a5g8c icdlwmnq"))]',

         ),
        "Comment responses visible")
    postResponses = Selector((
        '(//div[@aria-posinset="1"])[1]//span[contains(text(), "réponse")]',),
        "Responses to the post")
    postPagers = Selector((
        '(//div[@aria-posinset="1"])[1]//div[@aria-label="Voir les commentaires marqués comme indésirables"]',
        '//a[@aria-label="Voir les commentaires marqués comme indésirables"]',),
        "# dots to the post comments")

    # Page Blocker Selectors
    popUpBtn = Selector(('//div[@aria-label="Autres actions"]',
                         '//div[@aria-label="Voir les options"]'),
                        "Pop up button for blocking a page")

    blockBtn = Selector(('//span[text()="Bloquer la Page"]',
                         '//span[text()="Bloquer"]'),
                        "Block button for blocking a page")

    deblockBtn = Selector(('//span[text()="Débloquer la Page"]',), "Deblock button")

    confirmBlockBtn = Selector(('//div[@aria-label="Confirmer le blocage"]//span[text()="Confirmer"]',
                                '(//div[@aria-label="Confirmer"]//span[text()="Confirmer"])[last()]'),
                               "Block confirmation button for blocking a page")

    pageBlockDilog = Selector(('//span[text()="Confirmer le blocage"]',
                               '//span[contains(text(),"Bloquer")]'),
                              "Page block confirmation modal dialog")

    pageNotReachable = Selector(('//span[text()="Cette page n’est pas disponible"]',),
                                "Page is not reachable for blocking text")
    pageLikeButton = Selector((
        '//div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t pfnyh3mw d2edcug0 hpfvmrgz o8rfisnq"]//span[@class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7 ltmttdrg g0qnabr5"]',),
        "Page like button for blocker script")

    page_links = Selector(('//div[@class="qjjbsfad j83agx80"]//div[@class="p6qk8glf h6tavxlh"]/a',), "Page links")

    page_not_published = Selector(('//h3[text()="Visibilité de la Page"]/..//span[text()="Page non publiée"]',),
                                  "Page not published check element")

    page_status_modifier_button = Selector(
        ('//h3[text()="Visibilité de la Page"]/..//span[@class="fbSettingsListItemEditText"]',),
        "Page status modifier button")

    page_publish_radio = Selector(('//label[text()="Page publiée"]',), "Page status public radio")

    page_modification_save_button = Selector(('//input[@value="Enregistrer les modifications"]',),
                                             "Page modification save button")

    page_settings_iframe = Selector(
        ('//iframe[@class="k4urcfbm jgljxmt5 a8c37x1j izx4hr6d humdl8nn bn081pho gcieejh5"]',),
        "Iframe of the settings page")
    # For liking a publication using page news_feed
    publications_div = Selector(('//div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]',), 'Publications div')

    nf_react_btn = Selector(('(.//span[@class=" _18vi"])[1]',
                             './/div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t g5gj957u d2edcug0 hpfvmrgz rj1gh0hx buofh1pr n8tt0mok hyh9befq iuny7tx3 ipjc6fyt"]',
                             './/div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t d2edcug0 hpfvmrgz rj1gh0hx buofh1pr g5gj957u n8tt0mok hyh9befq iuny7tx3 ipjc6fyt"]'),
                            "Reaction button to react to the post in newsfeed page"
                            )

    nf_reacted_btn = Selector(('(.//div[@class="e71nayrh  _18vj"])[1]/span[@class="q9uorilb sf5mxxl7"]',
                               './/div[@aria-label="Supprimer J’aime"]'),
                              "Already reacted button check on news feed page"
                              )
