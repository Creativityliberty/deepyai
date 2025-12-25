"""
Pydantic schemas for structured outputs in Deepy AI.
These schemas define the structure for extracting data from various sources.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Ingredient(BaseModel):
    """An ingredient in a recipe."""
    name: str = Field(description="Name of the ingredient")
    quantity: str = Field(description="Quantity of the ingredient, including units")


class Recipe(BaseModel):
    """A cooking recipe with ingredients and instructions."""
    recipe_name: str = Field(description="The name of the recipe")
    prep_time_minutes: Optional[int] = Field(
        default=None,
        description="Optional time in minutes to prepare the recipe"
    )
    ingredients: List[Ingredient] = Field(description="List of ingredients")
    instructions: List[str] = Field(description="Step-by-step cooking instructions")


class InvoiceLineItem(BaseModel):
    """A single line item on an invoice."""
    description: str = Field(description="Description of the item or service")
    quantity: float = Field(description="Quantity of items")
    unit_price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price for this line item")


class Invoice(BaseModel):
    """An invoice document."""
    invoice_number: str = Field(description="Invoice number or ID")
    date: str = Field(description="Invoice date")
    vendor_name: str = Field(description="Name of the vendor/seller")
    customer_name: str = Field(description="Name of the customer/buyer")
    line_items: List[InvoiceLineItem] = Field(description="List of items on the invoice")
    subtotal: float = Field(description="Subtotal before tax")
    tax: Optional[float] = Field(default=None, description="Tax amount")
    total: float = Field(description="Total amount due")


class Feedback(BaseModel):
    """User feedback classification."""
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="Overall sentiment of the feedback"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of feedback (e.g., 'UI', 'Performance', 'Feature Request')"
    )
    summary: str = Field(description="Brief summary of the feedback")
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        default=None,
        description="Priority level for addressing this feedback"
    )


class DesignPatternExample(BaseModel):
    """An example implementation of a design pattern."""
    language: str = Field(description="Programming language (e.g., 'Python', 'Java', 'C++')")
    code: str = Field(description="Code example")
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of the code"
    )


class DesignPattern(BaseModel):
    """A software design pattern."""
    pattern_name: str = Field(description="Name of the design pattern")
    category: Literal["Creational", "Structural", "Behavioral"] = Field(
        description="Category of the pattern"
    )
    description: str = Field(description="Description of what the pattern does")
    use_cases: List[str] = Field(description="Common use cases for this pattern")
    advantages: List[str] = Field(description="Advantages of using this pattern")
    disadvantages: List[str] = Field(description="Disadvantages or limitations")
    examples: Optional[List[DesignPatternExample]] = Field(
        default=None,
        description="Code examples in various languages"
    )


class PDFSummary(BaseModel):
    """Summary of a PDF document."""
    title: str = Field(description="Title or main topic of the document")
    summary: str = Field(description="Comprehensive summary of the document")
    key_points: List[str] = Field(description="Key points or takeaways")
    page_count: Optional[int] = Field(
        default=None,
        description="Number of pages in the document"
    )
    document_type: Optional[str] = Field(
        default=None,
        description="Type of document (e.g., 'Research Paper', 'Invoice', 'Manual')"
    )


# Schema registry for easy access
SCHEMA_REGISTRY = {
    "recipe": Recipe,
    "invoice": Invoice,
    "feedback": Feedback,
    "design_pattern": DesignPattern,
    "pdf_summary": PDFSummary,
}


def get_schema(schema_type: str) -> type[BaseModel]:
    """Get a schema by its type name."""
    if schema_type not in SCHEMA_REGISTRY:
        raise ValueError(
            f"Unknown schema type: {schema_type}. "
            f"Available types: {', '.join(SCHEMA_REGISTRY.keys())}"
        )
    return SCHEMA_REGISTRY[schema_type]
