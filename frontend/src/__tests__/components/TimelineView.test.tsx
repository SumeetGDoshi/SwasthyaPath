/**
 * Tests for TimelineView component
 * Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
 * Phase 4: Frontend Component Tests
 */

import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { TimelineView } from '@/components/TimelineView'
import { TimelineEntry } from '@/types'

const mockEntries: TimelineEntry[] = [
  {
    id: '1',
    test_name: 'HbA1c',
    test_value: '5.8',
    test_unit: '%',
    test_date: '2024-11-15',
    status: 'normal',
    hospital_name: 'Apollo Hospital',
    is_duplicate: false,
    category: 'blood',
    reference_range: '4.0-5.6%',
  },
  {
    id: '2',
    test_name: 'Lipid Profile',
    test_value: '210',
    test_unit: 'mg/dL',
    test_date: '2024-10-15',
    status: 'abnormal',
    hospital_name: 'Max Hospital',
    is_duplicate: true,
    category: 'blood',
    reference_range: '<200 mg/dL',
  },
  {
    id: '3',
    test_name: 'X-Ray Chest',
    test_value: 'Normal',
    test_unit: '',
    test_date: '2024-09-15',
    status: 'normal',
    hospital_name: 'Fortis Hospital',
    is_duplicate: false,
    category: 'imaging',
    reference_range: '',
  },
]

describe('TimelineView', () => {
  describe('Loading State', () => {
    it('should show loading skeletons', () => {
      render(<TimelineView entries={[]} isLoading={true} />)
      
      // Should show skeleton cards with animate-pulse
      const skeletons = document.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no entries', () => {
      render(<TimelineView entries={[]} isLoading={false} />)
      expect(screen.getByText('No Tests Found')).toBeInTheDocument()
    })

    it('should show upload prompt in empty state', () => {
      render(<TimelineView entries={[]} isLoading={false} />)
      expect(screen.getByText(/Upload your first medical report/i)).toBeInTheDocument()
    })
  })

  describe('Timeline Rendering', () => {
    it('should render timeline entries', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('HbA1c')).toBeInTheDocument()
      expect(screen.getByText('Lipid Profile')).toBeInTheDocument()
      expect(screen.getByText('X-Ray Chest')).toBeInTheDocument()
    })

    it('should display test values', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('5.8')).toBeInTheDocument()
      expect(screen.getByText('210')).toBeInTheDocument()
    })

    it('should display test units', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('%')).toBeInTheDocument()
      expect(screen.getByText('mg/dL')).toBeInTheDocument()
    })

    it('should show duplicate badge for duplicate tests', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('Duplicate')).toBeInTheDocument()
    })

    it('should display hospital names', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('Apollo Hospital')).toBeInTheDocument()
      expect(screen.getByText('Max Hospital')).toBeInTheDocument()
    })
  })

  describe('Statistics', () => {
    it('should show total tests count', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('Total Tests')).toBeInTheDocument()
    })

    it('should show normal count', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('Normal')).toBeInTheDocument()
      // 2 normal tests (HbA1c and X-Ray)
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    it('should show abnormal/attention count', () => {
      render(<TimelineView entries={mockEntries} />)
      expect(screen.getByText('Need Attention')).toBeInTheDocument()
    })
  })

  describe('Filtering', () => {
    it('should have filter buttons', () => {
      render(<TimelineView entries={mockEntries} />)
      
      expect(screen.getByRole('button', { name: /All/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /blood/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /imaging/i })).toBeInTheDocument()
    })

    it('should filter by category', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Click imaging filter
      fireEvent.click(screen.getByRole('button', { name: /imaging/i }))
      
      // Only X-Ray should be visible
      expect(screen.getByText('X-Ray Chest')).toBeInTheDocument()
      // Blood tests should be filtered out
      expect(screen.queryByText('HbA1c')).not.toBeInTheDocument()
    })

    it('should have status filter buttons', () => {
      render(<TimelineView entries={mockEntries} />)
      
      expect(screen.getByRole('button', { name: /normal/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /abnormal/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /critical/i })).toBeInTheDocument()
    })

    it('should filter by status', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Click abnormal filter
      fireEvent.click(screen.getByRole('button', { name: /abnormal/i }))
      
      // Only Lipid Profile (abnormal) should be visible
      expect(screen.getByText('Lipid Profile')).toBeInTheDocument()
      expect(screen.queryByText('HbA1c')).not.toBeInTheDocument()
    })

    it('should reset filter when clicking All', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Apply filter
      fireEvent.click(screen.getByRole('button', { name: /imaging/i }))
      
      // Reset filter
      fireEvent.click(screen.getByRole('button', { name: /All/i }))
      
      // All entries should be visible
      expect(screen.getByText('HbA1c')).toBeInTheDocument()
      expect(screen.getByText('X-Ray Chest')).toBeInTheDocument()
    })
  })

  describe('Expandable Cards', () => {
    it('should expand card on click to show reference range', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Find and click the HbA1c card
      const hba1cElement = screen.getByText('HbA1c')
      const card = hba1cElement.closest('[class*="cursor-pointer"]')
      
      if (card) {
        fireEvent.click(card)
        // Reference range should be visible after click
        expect(screen.getByText(/Reference Range/)).toBeInTheDocument()
        expect(screen.getByText('4.0-5.6%')).toBeInTheDocument()
      }
    })
  })

  describe('Status Colors', () => {
    it('should display status badges', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Should have status badges
      expect(screen.getAllByText('normal')).toHaveLength(2) // 2 normal tests
      expect(screen.getByText('abnormal')).toBeInTheDocument()
    })
  })

  describe('Month Grouping', () => {
    it('should group entries by month', () => {
      render(<TimelineView entries={mockEntries} />)
      
      // Should show month headers
      expect(screen.getByText(/November 2024/i)).toBeInTheDocument()
      expect(screen.getByText(/October 2024/i)).toBeInTheDocument()
      expect(screen.getByText(/September 2024/i)).toBeInTheDocument()
    })
  })
})

describe('TimelineView Edge Cases', () => {
  it('should handle entries without test values', () => {
    const entryWithoutValue: TimelineEntry[] = [{
      id: '1',
      test_name: 'Test Without Value',
      test_date: '2024-11-15',
      status: 'normal',
      is_duplicate: false,
      category: 'other',
    }]
    
    render(<TimelineView entries={entryWithoutValue} />)
    expect(screen.getByText('Test Without Value')).toBeInTheDocument()
  })

  it('should handle entries without hospital name', () => {
    const entryWithoutHospital: TimelineEntry[] = [{
      id: '1',
      test_name: 'Test',
      test_date: '2024-11-15',
      status: 'normal',
      is_duplicate: false,
      category: 'blood',
    }]
    
    render(<TimelineView entries={entryWithoutHospital} />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('should handle single entry', () => {
    const singleEntry: TimelineEntry[] = [{
      id: '1',
      test_name: 'Single Test',
      test_date: '2024-11-15',
      status: 'normal',
      is_duplicate: false,
      category: 'blood',
    }]
    
    render(<TimelineView entries={singleEntry} />)
    expect(screen.getByText('Single Test')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument() // Total tests
  })
})


