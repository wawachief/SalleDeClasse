from PySide2.QtWidgets import QVBoxLayout, QLabel, QDialog
from PySide2.QtGui import QPixmap
from PySide2.QtCore import QSize, Qt

from src.assets_manager import AssetManager, tr


class AboutFrame(QDialog):

    # --- Init methods ---

    def __init__(self):
        """
        About-us frame.
        """
        QDialog.__init__(self)

        self.setWindowTitle(f"{tr('app_title')} | {tr('about_us')}")
        self.setFixedSize(QSize(600, 500))

        self.links_style = '<style>a { text-decoration:none; color:#416284; } </style>'
        self.contact_style = '<style>a { text-decoration:none; color:darkblue; } </style>'

        self._set_layout()

    def _set_layout(self):
        """
        Creates this Widget's Layout
        """
        box = QVBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)

        box.addSpacing(20)
        AboutLabel(f'<b>{tr("app_title")}</b> {tr("about_sdc")}', box)
        AboutLabel(f'{tr("about_features")} <b>Olivier Lécluse</b><br>'
                   f'{tr("about_ihm")} <b>Thomas Lécluse</b><br>'
                   f'{tr("about_web")} <b>Nicolas Lécluse</b>', box)

        logo = QLabel()
        logo.setPixmap(QPixmap("assets/LDC-dark.png"))
        logo.setFixedSize(QSize(512, 222))  # Original dimension is 2048x888, we divided by 4
        logo.setScaledContents(True)
        box.addWidget(logo)
        box.setAlignment(logo, Qt.AlignCenter)

        links = f'{tr("about_links")}<br>' \
                f'&nbsp;&nbsp;- <b><a href="https://sdc.lecluse.fr">{tr("about_doc")}</a></b><br>'\
                f'&nbsp;&nbsp;- <b><a href="https://github.com/wawachief/SalleDeClasse">{tr("about_github")}</a></b>'
        contact = f'{tr("about_contact")} <a href="mailto:devcorp@lecluse.fr">devcorp@lecluse.fr</a>'

        AboutLabel(f'{self.links_style}{links}', box, True, False)
        AboutLabel(f'<br><br>{self.contact_style}{contact}', box, True)
        AboutLabel(f'{self.links_style}<b><a href="https://www.gnu.org/licenses/gpl-3.0.fr.html">GPL-3.0 License</a></b>', box, True)
        AboutLabel(f"Version - {AssetManager.getInstance().config('main', 'version')}", box)

        box.addSpacing(20)

        self.setLayout(box)


class AboutLabel(QLabel):
    def __init__(self, text, layout, clickable=False, align_center=True):
        """
        Custom labels for about box
        """
        QLabel.__init__(self, text)

        self.setOpenExternalLinks(clickable)
        self.setAlignment(Qt.AlignCenter if align_center else Qt.AlignLeft)

        layout.addWidget(self)
        layout.setAlignment(self, Qt.AlignCenter)
