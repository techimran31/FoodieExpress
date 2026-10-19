// FoodieExpress — Money Formatting Unit Tests
import { money } from '../assets/js/config.js';

describe('money()', () => {
  test('formats zero', () => {
    expect(money(0)).toBe('₹0');
  });

  test('formats single digit', () => {
    expect(money(5)).toBe('₹5');
  });

  test('formats hundreds', () => {
    expect(money(249)).toBe('₹249');
  });

  test('formats thousands with separator', () => {
    expect(money(1250)).toBe('₹1,250');
  });

  test('formats large numbers', () => {
    expect(money(55000)).toBe('₹55,000');
  });

  test('formats decimals', () => {
    expect(money(249.50)).toBe('₹249.50');
  });

  test('handles negative numbers', () => {
    expect(money(-100)).toBe('₹-100');
  });

  test('returns string type', () => {
    expect(typeof money(100)).toBe('string');
  });
});