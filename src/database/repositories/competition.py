"""
Repositorio para competiciones.
"""

from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Competition, Event
from src.database.repositories.base import BaseRepository


class CompetitionRepository(BaseRepository[Competition]):
    """
    Repositorio para operaciones con competiciones.
    """
    
    model = Competition
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_pdf_url(self, pdf_url: str) -> Optional[Competition]:
        """Obtiene una competición por su URL de PDF."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.pdf_url == pdf_url)
            .options(selectinload(Competition.events))
        )
        return result.scalar_one_or_none()
    
    async def get_by_pdf_hash(self, pdf_hash: str) -> Optional[Competition]:
        """Obtiene una competición por su hash de PDF."""
        result = await self.session.execute(
            select(Competition).where(Competition.pdf_hash == pdf_hash)
        )
        return result.scalar_one_or_none()
    
    async def get_upcoming(
        self,
        from_date: Optional[date] = None,
    ) -> Sequence[Competition]:
        """
        Obtiene competiciones con fecha >= from_date.
        
        Si from_date es None, usa la fecha actual.
        """
        if from_date is None:
            from_date = date.today()
        
        result = await self.session.execute(
            select(Competition)
            .where(Competition.competition_date >= from_date)
            .order_by(Competition.competition_date)
            .options(selectinload(Competition.events))
        )
        return result.scalars().all()
    
    async def upsert_with_hash(
        self,
        pdf_url: str,
        pdf_hash: Optional[str],
        name: str,
        competition_date: date,
        location: str,
        has_modifications: bool = False,
        competition_type: Optional[str] = None,
        events: Optional[list[dict]] = None,
    ) -> tuple[Competition, bool]:
        """
        Inserta o actualiza una competición basándose en el hash del PDF.
        
        Si el PDF ya existe con el mismo hash, no hace nada.
        Si el PDF existe pero el hash cambió, actualiza.
        Si el PDF no existe, lo crea.
        
        Args:
            pdf_url: URL del PDF
            pdf_hash: Hash SHA-256 del contenido del PDF
            name: Nombre de la competición
            competition_date: Fecha de la competición
            location: Lugar
            has_modifications: Si tiene marcador de modificaciones
            competition_type: Tipo de competición (PC, AL, etc.)
            events: Lista opcional de eventos a crear
            
        Returns:
            Tupla (Competition, is_new_or_updated)
            - is_new_or_updated es True si se creó o actualizó
        """
        existing = await self.get_by_pdf_url(pdf_url)
        
        if existing:
            # Ya existe - verificar si el hash cambió
            if existing.pdf_hash == pdf_hash:
                # Sin cambios
                return existing, False
            
            # Hash diferente - actualizar
            await self.update(
                existing,
                pdf_hash=pdf_hash,
                name=name,
                competition_date=competition_date,
                location=location,
                has_modifications=has_modifications,
                competition_type=competition_type,
            )
            
            # Eliminar eventos antiguos y crear nuevos
            if events is not None:
                # Eliminar eventos existentes
                for event in list(existing.events):
                    await self.session.delete(event)
                
                # Crear nuevos eventos
                for event_data in events:
                    event = Event(
                        competition_id=existing.id,
                        **event_data
                    )
                    self.session.add(event)
            
            await self.session.flush()
            return existing, True
        
        # No existe - crear nueva
        competition = await self.create(
            pdf_url=pdf_url,
            pdf_hash=pdf_hash,
            name=name,
            competition_date=competition_date,
            location=location,
            has_modifications=has_modifications,
            competition_type=competition_type,
        )
        
        # Crear eventos
        if events is not None:
            for event_data in events:
                event = Event(
                    competition_id=competition.id,
                    **event_data
                )
                self.session.add(event)
            await self.session.flush()
        
        return competition, True
    
    async def get_with_events(self, competition_id: int) -> Optional[Competition]:
        """Obtiene una competición con sus eventos cargados."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.id == competition_id)
            .options(selectinload(Competition.events))
        )
        return result.scalar_one_or_none()
    
    async def count_upcoming(self, from_date: Optional[date] = None) -> int:
        """Cuenta competiciones futuras."""
        if from_date is None:
            from_date = date.today()
        
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(Competition.id))
            .where(Competition.competition_date >= from_date)
        )
        return result.scalar_one()
