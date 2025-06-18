
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import HexColor
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import base64

class FertilizationPDFGenerator:
    """Générateur de rapports PDF pour les plans de fertilisation"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Définit les styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=HexColor('#2E7D32'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#1976D2'),
            spaceAfter=15,
            spaceBefore=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#388E3C'),
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6,
            textColor=HexColor('#4A5568')
        ))
    
    def generate_fertilization_pdf(self, plan_data: Dict, farmer_info: Dict, 
                                 output_path: str = None) -> str:
        """Génère le rapport PDF complet"""
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"fertilization_plan_{timestamp}.pdf"
        
        # Création du document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construction du contenu
        story = []
        
        # En-tête
        story.extend(self._create_header(farmer_info, plan_data))
        
        # Résumé exécutif
        story.extend(self._create_executive_summary(plan_data))
        
        # Analyse du sol
        story.extend(self._create_soil_analysis(plan_data))
        
        # Programme de fertilisation
        story.extend(self._create_fertilization_program(plan_data))
        
        # Calendrier détaillé
        story.extend(self._create_detailed_schedule(plan_data))
        
        # Recommandations
        story.extend(self._create_recommendations(plan_data))
        
        # Estimation des coûts
        story.extend(self._create_cost_analysis(plan_data))
        
        # Graphiques et visualisations
        story.extend(self._create_charts(plan_data))
        
        # Annexes
        story.extend(self._create_appendices(plan_data))
        
        # Génération du PDF
        doc.build(story)
        
        return output_path
    
    def _create_header(self, farmer_info: Dict, plan_data: Dict) -> List:
        """Crée l'en-tête du document"""
        elements = []
        
        # Titre principal
        title = Paragraph(
            "PLAN DE FERTILISATION INTELLIGENT",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Informations agriculteur et exploitation
        header_data = [
            ['Agriculteur:', farmer_info.get('name', 'Non spécifié')],
            ['Exploitation:', farmer_info.get('farm_name', 'Non spécifiée')],
            ['Culture:', plan_data['crop_info']['name']],
            ['Superficie:', f"{farmer_info.get('area', 0)} hectares"],
            ['Date du plan:', datetime.now().strftime("%d/%m/%Y")],
            ['Stade actuel:', plan_data['crop_info']['current_stage']]
        ]
        
        header_table = Table(header_data, colWidths=[4*cm, 6*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#E8F5E8')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#2E7D32')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_executive_summary(self, plan_data: Dict) -> List:
        """Crée le résumé exécutif"""
        elements = []
        
        elements.append(Paragraph("RÉSUMÉ EXÉCUTIF", self.styles['CustomHeading']))
        
        # Métriques clés
        soil_quality = plan_data['soil_analysis']['soil_quality_score']
        total_cost = plan_data['total_cost_estimate']['total_cost_euros']
        
        summary_text = f"""
        <b>Qualité du sol:</b> {soil_quality:.1f}/100<br/>
        <b>Coût total estimé:</b> {total_cost:.2f} €<br/>
        <b>Nombre d'applications:</b> {len(plan_data['fertilization_schedule'])} stades<br/>
        <b>Optimisation IA:</b> {'Activée' if plan_data.get('ai_optimization') else 'Non disponible'}
        """
        
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_soil_analysis(self, plan_data: Dict) -> List:
        """Crée la section d'analyse du sol"""
        elements = []
        
        elements.append(Paragraph("ANALYSE DU SOL", self.styles['CustomHeading']))
        
        soil_analysis = plan_data['soil_analysis']
        
        # Tableau des disponibilités
        availability_data = [['Nutriment', 'Disponibilité (%)', 'Statut']]
        
        for nutrient, availability in soil_analysis['nutrient_availability'].items():
            percentage = availability * 100
            status = "Excellente" if percentage > 80 else \
                     "Bonne" if percentage > 60 else \
                     "Moyenne" if percentage > 40 else "Faible"
            
            availability_data.append([
                nutrient,
                f"{percentage:.1f}%",
                status
            ])
        
        availability_table = Table(availability_data, colWidths=[3*cm, 3*cm, 4*cm])
        availability_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        
        elements.append(availability_table)
        elements.append(Spacer(1, 15))
        
        # Score de qualité
        quality_text = f"<b>Score de qualité global:</b> {soil_analysis['soil_quality_score']:.1f}/100"
        elements.append(Paragraph(quality_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_fertilization_program(self, plan_data: Dict) -> List:
        """Crée le programme de fertilisation"""
        elements = []
        
        elements.append(Paragraph("PROGRAMME DE FERTILISATION", self.styles['CustomHeading']))
        
        # Tableau des besoins totaux
        nutrients_data = [['Nutriment', 'Besoin total (kg/ha)', 'Besoin ajusté (kg/ha)']]
        
        adjusted_nutrients = plan_data['adjusted_nutrients']
        
        for nutrient, amount in adjusted_nutrients.items():
            nutrients_data.append([
                nutrient,
                f"{amount / 1.2:.0f}",  # Estimation besoin de base
                f"{amount:.0f}"
            ])
        
        nutrients_table = Table(nutrients_data, colWidths=[3*cm, 4*cm, 4*cm])
        nutrients_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#388E3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        
        elements.append(nutrients_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_detailed_schedule(self, plan_data: Dict) -> List:
        """Crée le calendrier détaillé"""
        elements = []
        
        elements.append(Paragraph("CALENDRIER D'APPLICATION", self.styles['CustomHeading']))
        
        for stage in plan_data['fertilization_schedule']:
            # Titre du stade
            stage_title = f"{stage['stage'].title()} - {stage['stage_description']}"
            elements.append(Paragraph(stage_title, self.styles['CustomSubHeading']))
            
            # Tableau des applications pour ce stade
            app_data = [['Nutriment', 'Type d\'engrais', 'Dose (kg/ha)', 'Dose totale (kg)']]
            
            for app in stage['applications']:
                app_data.append([
                    app['nutrient'],
                    app['fertilizer_type'],
                    f"{app['amount_per_ha']:.1f}",
                    f"{app['total_amount']:.1f}"
                ])
            
            app_table = Table(app_data, colWidths=[2*cm, 5*cm, 2.5*cm, 2.5*cm])
            app_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E3F2FD')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
            ]))
            
            elements.append(app_table)
            
            # Recommandations de timing
            timing_text = "<b>Recommandations:</b><br/>"
            for rec in stage['timing_recommendations']:
                timing_text += f"• {rec}<br/>"
            
            elements.append(Paragraph(timing_text, self.styles['Recommendation']))
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _create_recommendations(self, plan_data: Dict) -> List:
        """Crée la section des recommandations"""
        elements = []
        
        elements.append(Paragraph("RECOMMANDATIONS SPÉCIFIQUES", self.styles['CustomHeading']))
        
        recommendations_text = ""
        for i, rec in enumerate(plan_data['recommendations'], 1):
            recommendations_text += f"{i}. {rec}<br/><br/>"
        
        elements.append(Paragraph(recommendations_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_cost_analysis(self, plan_data: Dict) -> List:
        """Crée l'analyse des coûts"""
        elements = []
        
        elements.append(Paragraph("ANALYSE DES COÛTS", self.styles['CustomHeading']))
        
        cost_data = plan_data['total_cost_estimate']
        
        # Tableau des coûts
        cost_table_data = [['Poste', 'Coût (€)']]
        
        for nutrient, cost in cost_data['cost_breakdown'].items():
            cost_table_data.append([f'Engrais {nutrient}', f"{cost:.2f}"])
        
        cost_table_data.append(['TOTAL', f"{cost_data['total_cost_euros']:.2f}"])
        cost_table_data.append(['Coût par hectare', f"{cost_data['cost_per_hectare']:.2f}"])
        
        cost_table = Table(cost_table_data, colWidths=[6*cm, 4*cm])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -2), (-1, -1), HexColor('#FFF3E0')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ]))
        
        elements.append(cost_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_charts(self, plan_data: Dict) -> List:
        """Crée les graphiques et visualisations"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("VISUALISATIONS", self.styles['CustomHeading']))
        
        # Graphique de répartition des nutriments
        chart_buffer = self._create_nutrients_chart(plan_data)
        if chart_buffer:
            img = Image(chart_buffer, width=15*cm, height=10*cm)
            elements.append(img)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_nutrients_chart(self, plan_data: Dict) -> io.BytesIO:
        """Crée un graphique de répartition des nutriments"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Graphique 1: Répartition des nutriments
            nutrients = list(plan_data['adjusted_nutrients'].keys())
            amounts = list(plan_data['adjusted_nutrients'].values())
            
            ax1.pie(amounts, labels=nutrients, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Répartition des Nutriments (%)')
            
            # Graphique 2: Coûts par nutriment
            cost_breakdown = plan_data['total_cost_estimate']['cost_breakdown']
            cost_nutrients = list(cost_breakdown.keys())
            cost_amounts = list(cost_breakdown.values())
            
            ax2.bar(cost_nutrients, cost_amounts, color=['#4CAF50', '#2196F3', '#FF9800'])
            ax2.set_title('Coûts par Nutriment (€)')
            ax2.set_ylabel('Coût (€)')
            
            plt.tight_layout()
            
            # Sauvegarde en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Erreur création graphique: {e}")
            return None
    
    def _create_appendices(self, plan_data: Dict) -> List:
        """Crée les annexes"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("ANNEXES", self.styles['CustomHeading']))
        
        # Méthodologie
        methodology_text = """
        <b>Méthodologie de calcul:</b><br/>
        Ce plan de fertilisation a été généré en utilisant:<br/>
        • Analyse des besoins spécifiques de la culture<br/>
        • Évaluation de la disponibilité des nutriments dans le sol<br/>
        • Correction basée sur les conditions pédoclimatiques<br/>
        • Optimisation par intelligence artificielle (si disponible)<br/><br/>
        
        <b>Sources des données:</b><br/>
        • Base de données des exigences culturales<br/>
        • Analyses de sol fournies<br/>
        • Prévisions météorologiques<br/>
        • Historique des pratiques agricoles
        """
        
        elements.append(Paragraph(methodology_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # Contact et support
        contact_text = """
        <b>Support technique:</b><br/>
        Pour toute question concernant ce plan de fertilisation,<br/>
        contactez notre équipe d'agronomes.<br/><br/>
        
        <b>Avertissement:</b><br/>
        Ce plan est généré automatiquement et doit être validé<br/>
        par un agronome qualifié avant application.
        """
        
        elements.append(Paragraph(contact_text, self.styles['CustomBody']))
        
        return elements

# Instance globale
pdf_generator = FertilizationPDFGenerator()
