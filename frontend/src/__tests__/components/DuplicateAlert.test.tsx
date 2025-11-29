/**
 * Tests for DuplicateAlert components
 * Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
 * Phase 4: Frontend Component Tests
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { DuplicateAlert, MultiDuplicateAlert } from '@/components/DuplicateAlert'
import { DuplicateAlert as DuplicateAlertType } from '@/types'
import * as api from '@/lib/api'

// Mock the API
jest.mock('@/lib/api', () => ({
  updateDuplicateDecision: jest.fn(),
}))

const mockAlert: DuplicateAlertType = {
  id: 'alert-123',
  user_id: 'user-123',
  new_test_name: 'HbA1c',
  original_test_date: '2024-10-15',
  days_since_original: 30,
  decision: 'pending',
  savings_amount: 700,
  alert_message: 'This test was done 30 days ago. Valid for 90 days.',
  created_at: '2024-11-15T10:00:00Z',
}

describe('DuplicateAlert', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(api.updateDuplicateDecision as jest.Mock).mockResolvedValue({
      success: true,
    })
  })

  it('should display alert when open', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('Duplicate Test Detected!')).toBeInTheDocument()
  })

  it('should display test name', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('HbA1c')).toBeInTheDocument()
  })

  it('should show savings amount', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText(/700/)).toBeInTheDocument()
    expect(screen.getByText('Potential Savings')).toBeInTheDocument()
  })

  it('should show days since original test', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('30 days ago')).toBeInTheDocument()
  })

  it('should show Potential Duplicate badge', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('Potential Duplicate')).toBeInTheDocument()
  })

  it('should display alert message', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText(/This test was done 30 days ago/)).toBeInTheDocument()
  })

  it('should have Skip Test button', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByRole('button', { name: /Skip Test/i })).toBeInTheDocument()
  })

  it('should have Proceed Anyway button', () => {
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByRole('button', { name: /Proceed Anyway/i })).toBeInTheDocument()
  })

  it('should call API and onDecision when Skip is clicked', async () => {
    const onDecision = jest.fn()
    const onClose = jest.fn()
    
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={onDecision}
        isOpen={true}
        onClose={onClose}
      />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Skip Test/i }))
    
    await waitFor(() => {
      expect(api.updateDuplicateDecision).toHaveBeenCalledWith('alert-123', 'skip')
    })
    
    await waitFor(() => {
      expect(onDecision).toHaveBeenCalledWith('skip')
    })
  })

  it('should call API and onDecision when Proceed is clicked', async () => {
    const onDecision = jest.fn()
    const onClose = jest.fn()
    
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={onDecision}
        isOpen={true}
        onClose={onClose}
      />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Proceed Anyway/i }))
    
    await waitFor(() => {
      expect(api.updateDuplicateDecision).toHaveBeenCalledWith('alert-123', 'proceed')
    })
  })

  it('should close dialog after decision', async () => {
    const onClose = jest.fn()
    
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={onClose}
      />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Skip Test/i }))
    
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })

  it('should handle API errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation()
    ;(api.updateDuplicateDecision as jest.Mock).mockRejectedValue(new Error('API Error'))
    
    render(
      <DuplicateAlert
        alert={mockAlert}
        onDecision={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Skip Test/i }))
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled()
    })
    
    consoleSpy.mockRestore()
  })
})

describe('MultiDuplicateAlert', () => {
  const mockAlerts: DuplicateAlertType[] = [
    mockAlert,
    {
      ...mockAlert,
      id: 'alert-456',
      new_test_name: 'Lipid Profile',
      savings_amount: 1000,
      days_since_original: 45,
    },
    {
      ...mockAlert,
      id: 'alert-789',
      new_test_name: 'CBC',
      savings_amount: 500,
      days_since_original: 15,
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
    ;(api.updateDuplicateDecision as jest.Mock).mockResolvedValue({
      success: true,
    })
  })

  it('should show progress indicator', () => {
    render(
      <MultiDuplicateAlert
        alerts={mockAlerts}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('1 of 3')).toBeInTheDocument()
  })

  it('should show first alert initially', () => {
    render(
      <MultiDuplicateAlert
        alerts={mockAlerts}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('HbA1c')).toBeInTheDocument()
  })

  it('should show total savings', () => {
    render(
      <MultiDuplicateAlert
        alerts={mockAlerts}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    // Total: 700 + 1000 + 500 = 2200
    expect(screen.getByText(/2,200/)).toBeInTheDocument()
  })

  it('should advance to next alert on decision', async () => {
    render(
      <MultiDuplicateAlert
        alerts={mockAlerts}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    // Skip first alert
    fireEvent.click(screen.getByRole('button', { name: /Skip/i }))
    
    await waitFor(() => {
      expect(screen.getByText('2 of 3')).toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('Lipid Profile')).toBeInTheDocument()
    })
  })

  it('should call onComplete after last alert', async () => {
    const onComplete = jest.fn()
    const onClose = jest.fn()
    
    render(
      <MultiDuplicateAlert
        alerts={[mockAlert]} // Single alert
        onComplete={onComplete}
        isOpen={true}
        onClose={onClose}
      />
    )
    
    fireEvent.click(screen.getByRole('button', { name: /Skip/i }))
    
    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled()
    })
    
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })

  it('should show Duplicate Tests Found title', () => {
    render(
      <MultiDuplicateAlert
        alerts={mockAlerts}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    expect(screen.getByText('Duplicate Tests Found!')).toBeInTheDocument()
  })

  it('should handle proceeding through all alerts', async () => {
    const onComplete = jest.fn()
    
    render(
      <MultiDuplicateAlert
        alerts={[mockAlert, { ...mockAlert, id: 'alert-2', new_test_name: 'Test 2' }]}
        onComplete={onComplete}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    // First alert
    fireEvent.click(screen.getByRole('button', { name: /Proceed/i }))
    
    await waitFor(() => {
      expect(screen.getByText('Test 2')).toBeInTheDocument()
    })
    
    // Second alert
    fireEvent.click(screen.getByRole('button', { name: /Proceed/i }))
    
    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled()
    })
  })

  it('should return null if no current alert', () => {
    const { container } = render(
      <MultiDuplicateAlert
        alerts={[]}
        onComplete={jest.fn()}
        isOpen={true}
        onClose={jest.fn()}
      />
    )
    
    // Dialog should not render with empty alerts
    expect(container.querySelector('[role="dialog"]')).toBeNull()
  })
})


