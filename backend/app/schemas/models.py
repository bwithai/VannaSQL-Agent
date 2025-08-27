from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Integer, String, Text
from sqlmodel import Field, SQLModel


class DisciplineData(SQLModel, table=True):
    __tablename__ = "discipline_data"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, comment="Primary key"),
    )

    doc: Optional[date] = Field(
        default=None,
        sa_column=Column(
            Date,
            comment="Date of commission / date of joining",
        ),
    )

    cat: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(255),
            comment="Category of offence (e.g., violation of SOP)",
        ),
    )

    date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            comment="Exact initiation datetime when punishment was initiated (yyyy-mm-dd 00:00:00)",
        ),
    )

    arm: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(128),
            comment="Employment/arm reflecting war fighting capability",
        ),
    )

    course: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(64),
            comment="Unique batch number on passing out from academy",
            index=True,
        ),
    )

    svc_no: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(64),
            comment="Unique service number (e.g., PA-12345)",
            index=True,
        ),
    )

    rank: Optional[str] = Field(
        default=None,
        sa_column=Column(String(64), comment="Rank of the person"),
    )

    name: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), comment="Name of the person", index=True),
    )

    initiated_by: Optional[str] = Field(
        default=None,
        sa_column=Column(
            String(255),
            comment="Unit/formation who initiated this punishment (organization name)",
        ),
    )

    award: Optional[str] = Field(
        default=None,
        sa_column=Column(
            Text,
            comment=(
                "Punishment awarded by formation/HQ (e.g., severe displeasure, "
                "warning, reprimand)"
            ),
        ),
    )

    year: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, comment="Year when the punishment was initiated (e.g., 2020)", index=True),
    )

    svc_bracket: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, comment="Service in years at time when punishment was given (e.g., 5)"),
    )

    unit: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), comment="Unit where the person received the punishment"),
    )


def seed_discipline_data(session) -> None:
    """Populate DisciplineData table with dummy records."""
    from sqlmodel import select
    
    # Check if data already exists
    # existing = session.exec(select(DisciplineData)).first()
    # if existing:
    #     print("DisciplineData already seeded, skipping...")
    #     return
    
    dummy_records = [
        DisciplineData(
            doc=date(2015, 6, 15),
            cat="Violation of SOP",
            initiation_date=datetime(2020, 3, 15, 10, 30, 0),
            arm="Infantry",
            course="IMA-2015-A",
            svc_no="PA-12345",
            rank="Captain",
            name="John Smith",
            parent_unit="1st Battalion Rajput Regiment",
            initiated_by="HQ Western Command",
            award="Warning",
            initiation_year=2020,
            svc_bracket=5,
            awardee_unit="3rd Infantry Division"
        ),
        DisciplineData(
            doc=date(2018, 12, 10),
            cat="Absence without leave",
            initiation_date=datetime(2023, 8, 22, 14, 0, 0),
            arm="Artillery",
            course="OTA-2018-B",
            svc_no="LT-67890",
            rank="Lieutenant",
            name="Raj Kumar Singh",
            parent_unit="4th Field Artillery Regiment",
            initiated_by="Area HQ Central Command",
            award="Severe displeasure",
            initiation_year=2022,
            svc_bracket=5,
            awardee_unit="15th Artillery Brigade"
        ),
        DisciplineData(
            doc=date(2016, 8, 20),
            cat="Negligence of duty",
            initiation_date=datetime(2021, 11, 5, 9, 15, 0),
            arm="Armoured Corps",
            course="ACC-2016-C",
            svc_no="MJ-54321",
            rank="Major",
            name="Vikram Sharma",
            parent_unit="17th Poona Horse",
            initiated_by="HQ Southern Command",
            award="Reprimand",
            initiation_year=2021,
            svc_bracket=5,
            awardee_unit="31st Armoured Division"
        ),
        DisciplineData(
            doc=date(2017, 4, 3),
            cat="Misconduct",
            initiation_date=datetime(2022, 1, 18, 16, 45, 0),
            arm="Engineers",
            course="MES-2017-D",
            svc_no="CP-98765",
            rank="Colonel",
            name="Amit Patel",
            parent_unit="2nd Engineer Regiment",
            initiated_by="HQ Eastern Command",
            award="Censure",
            initiation_year=2022,
            svc_bracket=5,
            awardee_unit="Corps of Engineers"
        ),
        DisciplineData(
            doc=date(2019, 1, 25),
            cat="Insubordination",
            initiation_date=datetime(2024, 2, 10, 11, 20, 0),
            arm="Signals",
            course="SIG-2019-E",
            svc_no="SG-13579",
            rank="Subedar",
            name="Ramesh Chandra",
            parent_unit="7th Signal Regiment",
            initiated_by="Corps HQ XIV Corps",
            award="Reduction in rank",
            initiation_year=2024,
            svc_bracket=5,
            awardee_unit="Signal Training Establishment"
        )
    ]
    
    session.add_all(dummy_records)
    session.commit()
    print(f"Seeded {len(dummy_records)} discipline records")


def seed_inventory_data(session) -> None:
    """Main seeding function called by db.py init"""
    seed_discipline_data(session)


