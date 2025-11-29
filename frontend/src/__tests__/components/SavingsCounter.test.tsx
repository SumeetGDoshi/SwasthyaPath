/**
 * Tests for SavingsCounter component
 * Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
 * Phase 4: Frontend Component Tests
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { SavingsCounter, SavingsCounterCompact } from '@/components/SavingsCounter'

describe('SavingsCounter', () => {
  it('should show "No Savings Yet" when total is 0', () => {
    render(<SavingsCounter totalSavings={0} testsSkipped={0} />)
    expect(screen.getByText('No Savings Yet')).toBeInTheDocument()
  })

  it('should show upload prompt when no savings', () => {
    render(<SavingsCounter totalSavings={0} testsSkipped={0} />)
    expect(screen.getByText(/Upload reports to detect duplicates/i)).toBeInTheDocument()
  })

  it('should display total savings amount', () => {
    render(
      <SavingsCounter 
        totalSavings={2100} 
        testsSkipped={3} 
        animated={false}
      />
    )
    expect(screen.getByText(/2,100/)).toBeInTheDocument()
  })

  it('should display tests skipped badge', () => {
    render(
      <SavingsCounter 
        totalSavings={1000} 
        testsSkipped={2} 
        animated={false}
      />
    )
    expect(screen.getByText('2 tests skipped')).toBeInTheDocument()
  })

  it('should not show tests skipped when zero', () => {
    render(
      <SavingsCounter 
        totalSavings={1000} 
        testsSkipped={0} 
        animated={false}
      />
    )
    expect(screen.queryByText(/tests skipped/)).not.toBeInTheDocument()
  })

  it('should display Total Savings label', () => {
    render(
      <SavingsCounter 
        totalSavings={500} 
        testsSkipped={1}
        animated={false}
      />
    )
    expect(screen.getByText('Total Savings')).toBeInTheDocument()
  })

  it('should show breakdown button when provided', () => {
    const breakdown = [
      { test_name: 'HbA1c', date_skipped: '2024-11-15', amount_saved: 700 },
    ]
    
    render(
      <SavingsCounter 
        totalSavings={700} 
        testsSkipped={1}
        breakdown={breakdown}
        animated={false}
      />
    )
    
    expect(screen.getByText('View breakdown')).toBeInTheDocument()
  })

  it('should expand breakdown on click', () => {
    const breakdown = [
      { test_name: 'HbA1c', date_skipped: '2024-11-15', amount_saved: 700 },
      { test_name: 'Lipid Profile', date_skipped: '2024-11-10', amount_saved: 1000 },
    ]
    
    render(
      <SavingsCounter 
        totalSavings={1700} 
        testsSkipped={2}
        breakdown={breakdown}
        animated={false}
      />
    )
    
    // Click to expand breakdown
    fireEvent.click(screen.getByText('View breakdown'))
    
    // Should show test names
    expect(screen.getByText('HbA1c')).toBeInTheDocument()
    expect(screen.getByText('Lipid Profile')).toBeInTheDocument()
  })

  it('should show achievement badge for 3+ tests skipped', () => {
    render(
      <SavingsCounter 
        totalSavings={2000} 
        testsSkipped={3}
        animated={false}
      />
    )
    expect(screen.getByText(/Smart Saver/)).toBeInTheDocument()
  })

  it('should not show achievement badge for less than 3 tests', () => {
    render(
      <SavingsCounter 
        totalSavings={1000} 
        testsSkipped={2}
        animated={false}
      />
    )
    expect(screen.queryByText(/Smart Saver/)).not.toBeInTheDocument()
  })

  it('should handle large savings amounts', () => {
    render(
      <SavingsCounter 
        totalSavings={100000} 
        testsSkipped={10}
        animated={false}
      />
    )
    expect(screen.getByText(/1,00,000/)).toBeInTheDocument()
  })
})

describe('SavingsCounterCompact', () => {
  it('should return null when no savings', () => {
    const { container } = render(
      <SavingsCounterCompact totalSavings={0} testsSkipped={0} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('should show compact savings display', () => {
    render(
      <SavingsCounterCompact totalSavings={1000} testsSkipped={2} />
    )
    expect(screen.getByText(/1,000/)).toBeInTheDocument()
    expect(screen.getByText(/saved/)).toBeInTheDocument()
  })

  it('should format currency correctly', () => {
    render(
      <SavingsCounterCompact totalSavings={50000} testsSkipped={5} />
    )
    expect(screen.getByText(/50,000/)).toBeInTheDocument()
  })
})


