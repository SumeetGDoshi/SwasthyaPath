/**
 * Tests for utility functions
 * Plan: /Users/sums/mcpDocs/plans/2025-11-27-write-comprehensive-test-cases-for-the-swasthyapat.md
 * Phase 3: Frontend Utility Tests
 */

import {
  cn,
  formatCurrency,
  formatDate,
  formatDateTime,
  daysAgo,
  getRelativeTime,
  getStatusColor,
  getStatusVariant,
  getCategoryIcon,
  isValidFileType,
  isValidFileSize,
  fileToBase64,
  truncate,
  generateDemoUserId,
  getUserId,
  setUserId,
} from '@/lib/utils'

describe('cn (className merger)', () => {
  it('should merge class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
  })

  it('should handle conditional classes', () => {
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz')
  })

  it('should handle undefined and null', () => {
    expect(cn('foo', undefined, 'bar', null)).toBe('foo bar')
  })

  it('should override conflicting Tailwind classes', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4')
    expect(cn('bg-red-500', 'bg-blue-500')).toBe('bg-blue-500')
  })

  it('should handle array inputs', () => {
    expect(cn(['foo', 'bar'])).toBe('foo bar')
  })

  it('should handle object inputs', () => {
    expect(cn({ foo: true, bar: false, baz: true })).toBe('foo baz')
  })
})

describe('formatCurrency', () => {
  it('should format numbers as INR', () => {
    expect(formatCurrency(1000)).toBe('₹1,000')
  })

  it('should use Indian number formatting for lakhs', () => {
    expect(formatCurrency(100000)).toBe('₹1,00,000')
  })

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('₹0')
  })

  it('should round decimals', () => {
    expect(formatCurrency(1234.56)).toBe('₹1,235')
    expect(formatCurrency(1234.44)).toBe('₹1,234')
  })

  it('should handle large numbers', () => {
    expect(formatCurrency(10000000)).toBe('₹1,00,00,000')
  })

  it('should handle negative numbers', () => {
    const result = formatCurrency(-1000)
    expect(result).toMatch(/-?₹1,000/)
  })
})

describe('formatDate', () => {
  it('should format date strings', () => {
    const result = formatDate('2024-11-15')
    expect(result).toMatch(/15/)
    expect(result).toMatch(/Nov/i)
    expect(result).toMatch(/2024/)
  })

  it('should handle ISO date strings', () => {
    const result = formatDate('2024-11-15T10:30:00Z')
    expect(result).toMatch(/15/)
  })

  it('should format different months correctly', () => {
    expect(formatDate('2024-01-01')).toMatch(/Jan/i)
    expect(formatDate('2024-06-15')).toMatch(/Jun/i)
    expect(formatDate('2024-12-25')).toMatch(/Dec/i)
  })
})

describe('formatDateTime', () => {
  it('should include time in format', () => {
    const result = formatDateTime('2024-11-15T10:30:00Z')
    expect(result).toMatch(/15/)
    expect(result).toMatch(/Nov/i)
    // Should have time component
    expect(result).toMatch(/\d{1,2}:\d{2}/)
  })
})

describe('daysAgo', () => {
  it('should return 0 for today', () => {
    const today = new Date().toISOString()
    expect(daysAgo(today)).toBeLessThanOrEqual(1)
  })

  it('should return 1 for yesterday', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    expect(daysAgo(yesterday.toISOString())).toBe(1)
  })

  it('should calculate days correctly', () => {
    const fiveDaysAgo = new Date()
    fiveDaysAgo.setDate(fiveDaysAgo.getDate() - 5)
    expect(daysAgo(fiveDaysAgo.toISOString())).toBe(5)
  })

  it('should handle dates far in the past', () => {
    const longAgo = new Date()
    longAgo.setDate(longAgo.getDate() - 365)
    expect(daysAgo(longAgo.toISOString())).toBeGreaterThanOrEqual(365)
  })
})

describe('getRelativeTime', () => {
  it('should return "Today" for today', () => {
    expect(getRelativeTime(new Date().toISOString())).toBe('Today')
  })

  it('should return "Yesterday" for yesterday', () => {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    expect(getRelativeTime(yesterday.toISOString())).toBe('Yesterday')
  })

  it('should return "X days ago" for recent dates', () => {
    const fiveDaysAgo = new Date()
    fiveDaysAgo.setDate(fiveDaysAgo.getDate() - 5)
    expect(getRelativeTime(fiveDaysAgo.toISOString())).toBe('5 days ago')
  })

  it('should return weeks ago for dates 1-4 weeks old', () => {
    const twoWeeksAgo = new Date()
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14)
    expect(getRelativeTime(twoWeeksAgo.toISOString())).toBe('2 weeks ago')
  })

  it('should return months ago for older dates', () => {
    const twoMonthsAgo = new Date()
    twoMonthsAgo.setDate(twoMonthsAgo.getDate() - 60)
    expect(getRelativeTime(twoMonthsAgo.toISOString())).toBe('2 months ago')
  })

  it('should return years ago for very old dates', () => {
    const twoYearsAgo = new Date()
    twoYearsAgo.setDate(twoYearsAgo.getDate() - 730)
    expect(getRelativeTime(twoYearsAgo.toISOString())).toBe('2 years ago')
  })
})

describe('getStatusColor', () => {
  it('should return correct color class for normal', () => {
    expect(getStatusColor('normal')).toBe('status-normal')
  })

  it('should return correct color class for abnormal', () => {
    expect(getStatusColor('abnormal')).toBe('status-abnormal')
  })

  it('should return correct color class for critical', () => {
    expect(getStatusColor('critical')).toBe('status-critical')
  })

  it('should handle case insensitivity', () => {
    expect(getStatusColor('NORMAL')).toBe('status-normal')
    expect(getStatusColor('Normal')).toBe('status-normal')
  })

  it('should return gray for unknown status', () => {
    expect(getStatusColor('unknown')).toContain('gray')
    expect(getStatusColor('')).toContain('gray')
  })
})

describe('getStatusVariant', () => {
  it('should return correct variant for normal', () => {
    expect(getStatusVariant('normal')).toBe('default')
  })

  it('should return correct variant for abnormal', () => {
    expect(getStatusVariant('abnormal')).toBe('secondary')
  })

  it('should return correct variant for critical', () => {
    expect(getStatusVariant('critical')).toBe('destructive')
  })

  it('should return outline for unknown', () => {
    expect(getStatusVariant('unknown')).toBe('outline')
  })
})

describe('getCategoryIcon', () => {
  it('should return Droplet for blood', () => {
    expect(getCategoryIcon('blood')).toBe('Droplet')
  })

  it('should return Scan for imaging', () => {
    expect(getCategoryIcon('imaging')).toBe('Scan')
  })

  it('should return Heart for vitals', () => {
    expect(getCategoryIcon('vitals')).toBe('Heart')
  })

  it('should return FlaskConical for urine', () => {
    expect(getCategoryIcon('urine')).toBe('FlaskConical')
  })

  it('should return FileText for unknown', () => {
    expect(getCategoryIcon('other')).toBe('FileText')
    expect(getCategoryIcon('unknown')).toBe('FileText')
  })
})

describe('isValidFileType', () => {
  it('should accept JPEG files', () => {
    const jpegFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileType(jpegFile)).toBe(true)
  })

  it('should accept JPG files', () => {
    const jpgFile = new File([''], 'test.jpg', { type: 'image/jpg' })
    expect(isValidFileType(jpgFile)).toBe(true)
  })

  it('should accept PNG files', () => {
    const pngFile = new File([''], 'test.png', { type: 'image/png' })
    expect(isValidFileType(pngFile)).toBe(true)
  })

  it('should accept PDF files', () => {
    const pdfFile = new File([''], 'test.pdf', { type: 'application/pdf' })
    expect(isValidFileType(pdfFile)).toBe(true)
  })

  it('should reject text files', () => {
    const textFile = new File([''], 'test.txt', { type: 'text/plain' })
    expect(isValidFileType(textFile)).toBe(false)
  })

  it('should reject HTML files', () => {
    const htmlFile = new File([''], 'test.html', { type: 'text/html' })
    expect(isValidFileType(htmlFile)).toBe(false)
  })

  it('should reject Word documents', () => {
    const docFile = new File([''], 'test.docx', { 
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
    })
    expect(isValidFileType(docFile)).toBe(false)
  })
})

describe('isValidFileSize', () => {
  it('should accept files under 10MB by default', () => {
    const smallFile = new File(['x'.repeat(1024)], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileSize(smallFile)).toBe(true)
  })

  it('should accept files exactly at limit', () => {
    const content = new Array(10 * 1024 * 1024).fill('x').join('')
    const exactFile = new File([content], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileSize(exactFile)).toBe(true)
  })

  it('should reject files over 10MB', () => {
    const largeContent = new Array(11 * 1024 * 1024).fill('x').join('')
    const largeFile = new File([largeContent], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileSize(largeFile)).toBe(false)
  })

  it('should accept custom size limit', () => {
    const content = new Array(3 * 1024 * 1024).fill('x').join('')
    const file = new File([content], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileSize(file, 5)).toBe(true)
    expect(isValidFileSize(file, 2)).toBe(false)
  })

  it('should accept empty files', () => {
    const emptyFile = new File([], 'test.jpg', { type: 'image/jpeg' })
    expect(isValidFileSize(emptyFile)).toBe(true)
  })
})

describe('truncate', () => {
  it('should truncate long strings', () => {
    expect(truncate('Hello World', 5)).toBe('Hello...')
  })

  it('should not truncate short strings', () => {
    expect(truncate('Hi', 10)).toBe('Hi')
  })

  it('should handle exact length', () => {
    expect(truncate('Hello', 5)).toBe('Hello')
  })

  it('should handle empty string', () => {
    expect(truncate('', 5)).toBe('')
  })

  it('should handle zero max length', () => {
    expect(truncate('Hello', 0)).toBe('...')
  })
})

describe('generateDemoUserId', () => {
  it('should generate unique IDs', () => {
    const id1 = generateDemoUserId()
    const id2 = generateDemoUserId()
    expect(id1).not.toBe(id2)
  })

  it('should have demo-user prefix', () => {
    const id = generateDemoUserId()
    expect(id).toMatch(/^demo-user-/)
  })

  it('should contain timestamp', () => {
    const before = Date.now()
    const id = generateDemoUserId()
    const after = Date.now()
    
    const timestamp = parseInt(id.replace('demo-user-', ''))
    expect(timestamp).toBeGreaterThanOrEqual(before)
    expect(timestamp).toBeLessThanOrEqual(after)
  })
})

describe('getUserId', () => {
  beforeEach(() => {
    (window.localStorage.getItem as jest.Mock).mockReturnValue(null)
  })

  it('should return demo user id by default', () => {
    expect(getUserId()).toBe('demo-user-123')
  })

  it('should return stored user id when exists', () => {
    (window.localStorage.getItem as jest.Mock).mockReturnValue('custom-user')
    expect(getUserId()).toBe('custom-user')
  })

  it('should store default user id when not found', () => {
    getUserId()
    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      'swasthya_user_id',
      'demo-user-123'
    )
  })
})

describe('setUserId', () => {
  it('should store user id in localStorage', () => {
    setUserId('new-user-456')
    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      'swasthya_user_id',
      'new-user-456'
    )
  })

  it('should handle empty string', () => {
    setUserId('')
    expect(window.localStorage.setItem).toHaveBeenCalledWith(
      'swasthya_user_id',
      ''
    )
  })
})


