from PySide2.QtWidgets import QVBoxLayout, QLabel, QDialog, QGridLayout
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QSize, Qt

from src.assets_manager import AssetManager, tr


class AboutFrame(QDialog):

    # --- Init methods ---

    def __init__(self, bdd_version: str):
        """
        About-us frame.

        :param bdd_version: current BDD version
        """
        QDialog.__init__(self)

        self.setWindowTitle(f"{tr('app_title')} | {tr('about_us')}")
        self.setFixedSize(QSize(600, 500))

        self.bdd_version = bdd_version

        self.links_style = "<style>a { text-decoration:none; color:#416284; font-weight: bold;}</style>"

        self._set_labels_and_layout()
        self.setStyleSheet("QDialog {background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, "
                           "stop: 0 #E0E0E0, stop: 0.2 #EAEAEA, stop: 0.5 #F0F0F0, stop: 0.8 #EAEAEA, "
                           "stop: 1 #E0E0E0); color: black;}")

    def _set_labels_and_layout(self):
        """
        Creates this Widget's content and layout
        """
        # --- Content ---

        # Lecluse DevCorp. Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/LDC-dark.png"))
        logo.setFixedSize(QSize(512, 222))  # Original dimension is 2048x888, we divided by 4
        logo.setScaledContents(True)

        # App credo
        lab_app = QLabel(f'<b>{tr("app_title")}</b> {tr("about_sdc")}')

        # Devs
        features_lab = QLabel(tr("about_features"))
        ihm_lab = QLabel(tr("about_ihm"))
        web_lab = QLabel(tr("about_web"))
        features_dev = QLabel(f'{self.links_style}<a href="https://www.google.fr">Olivier Lécluse</a>')
        features_dev.setOpenExternalLinks(True)
        ihm_dev = QLabel(
            f'{self.links_style}<a href="https://www.linkedin.com/in/thomas-lécluse-62130395/">Thomas Lécluse</a>')
        ihm_dev.setOpenExternalLinks(True)
        web_dev = QLabel(
            f'{self.links_style}<a href="https://www.linkedin.com/in/nicolas-lecluse-a3488752/">Nicolas Lécluse</a>')
        web_dev.setOpenExternalLinks(True)

        # Documentation link
        lab_link_doc = QLabel(
            f'{tr("link_to")} {self.links_style}<a href="https://sdc.lecluse.fr">{tr("about_doc")}</a>')
        lab_link_doc.setOpenExternalLinks(True)

        # Github link
        lab_link_git = QLabel(
            f'{tr("link_to")} {self.links_style}<a href="https://github.com/wawachief/SalleDeClasse">{tr("about_github")}</a>')
        lab_link_git.setOpenExternalLinks(True)

        # Contact
        lab_contact = QLabel(
            f'{tr("about_contact")} {self.links_style}<a href="mailto:devcorp@lecluse.fr">devcorp@lecluse.fr</a>')
        lab_contact.setOpenExternalLinks(True)

        # License
        lab_license = QLabel(
            f'{self.links_style}<a href="https://www.gnu.org/licenses/gpl-3.0.fr.html">GPL-3.0 License</a>')
        lab_license.setOpenExternalLinks(True)

        # Version
        lab_app_version = QLabel(tr("app_version"))
        lab_bdd_version = QLabel(tr("bdd_version"))
        app_version = QLabel(AssetManager.getInstance().config('main', 'version'))
        bdd_version = QLabel(str(self.bdd_version))

        # --- Layout ---
        box = QVBoxLayout()
        box.setMargin(0)
        box.setSpacing(0)

        # Logo
        box.addWidget(logo, alignment=Qt.AlignCenter)

        Separator(self.width() // 1.2, box)  # ----

        # 'Salle de Classe' credo
        box.addWidget(lab_app, alignment=Qt.AlignCenter)
        box.addSpacing(10)

        # Devs roles
        dev_grid = QGridLayout()
        dev_grid.setContentsMargins(0, 0, 0, 0)
        dev_grid.addWidget(features_lab, 0, 0, alignment=Qt.AlignRight)
        dev_grid.addWidget(ihm_lab, 1, 0, alignment=Qt.AlignRight)
        dev_grid.addWidget(web_lab, 2, 0, alignment=Qt.AlignRight)
        dev_grid.addWidget(features_dev, 0, 1, alignment=Qt.AlignLeft)
        dev_grid.addWidget(ihm_dev, 1, 1, alignment=Qt.AlignLeft)
        dev_grid.addWidget(web_dev, 2, 1, alignment=Qt.AlignLeft)
        box.addLayout(dev_grid)

        # Contact
        box.addSpacing(10)
        box.addWidget(lab_contact, alignment=Qt.AlignCenter)

        Separator(self.width() // 1.2, box)  # ----

        # Links of doc, git and license
        box.addWidget(lab_link_doc, alignment=Qt.AlignCenter)
        box.addWidget(lab_link_git, alignment=Qt.AlignCenter)
        box.addWidget(lab_license, alignment=Qt.AlignCenter)

        Separator(self.width() // 1.2, box)  # ----

        # Version
        grid_version = QGridLayout()
        grid_version.addWidget(lab_app_version, 0, 0, alignment=Qt.AlignRight)
        grid_version.addWidget(lab_bdd_version, 1, 0, alignment=Qt.AlignRight)
        grid_version.addWidget(app_version, 0, 1, alignment=Qt.AlignLeft)
        grid_version.addWidget(bdd_version, 1, 1, alignment=Qt.AlignLeft)
        box.addLayout(grid_version)
        box.addSpacing(10)

        self.setLayout(box)


class Separator(QLabel):

    def __init__(self, width, box: QVBoxLayout):
        """
        Separator for the about box
        """
        QLabel.__init__(self)

        self.setFixedHeight(3)
        self.setFixedWidth(int(width))
        self.setStyleSheet("background: QLinearGradient(x1: 0, y1: 0, x2: 1, y2: 0, "
                                   "stop: 0 #283747, stop: 0.25 #1A5276, stop: 0.5 #2980B9, "
                                   "stop: 0.75 #1A5276, stop: 1 #283747);")

        # Layout
        self.setAlignment(Qt.AlignCenter)
        box.addSpacing(10)
        box.addWidget(self, alignment=Qt.AlignCenter)
        box.addSpacing(10)
