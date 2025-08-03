# Contributing to Autonomous Trading Bot

Thank you for your interest in contributing to the Autonomous Trading Bot! This document provides guidelines for contributing to the project.

## 🎯 **Getting Started**

### **Prerequisites**
- Python 3.9+
- PHP 8.1+
- Node.js 16+
- Composer
- Git

### **Development Setup**
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/autonomous-trading-bot.git`
3. Set up the development environment:
   ```bash
   cd autonomous-trading-bot
   ./start_complete_system.sh
   ```

## 🔄 **Development Workflow**

### **Branch Naming**
- **Features**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-fix`
- **Documentation**: `docs/description-of-update`
- **Refactoring**: `refactor/description-of-refactor`

### **Commit Messages**
Follow conventional commit format:
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Scope: backend, frontend, docs, ci, config

Examples:
feat(backend): add new trading algorithm
fix(frontend): resolve dashboard connection issue
docs(readme): update setup instructions
```

## 📝 **Code Style Guidelines**

### **Python (Backend)**
- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for all functions and classes

```python
def calculate_position_size(balance: float, risk_percent: float = 0.01) -> float:
    """
    Calculate position size based on account balance and risk percentage.
    
    Args:
        balance: Current account balance
        risk_percent: Percentage of balance to risk per trade
        
    Returns:
        Position size in dollars
    """
    return balance * risk_percent
```

### **PHP (Frontend)**
- Follow PSR-12 coding standard
- Use meaningful variable and method names
- Add DocBlocks for all public methods
- Use Laravel best practices

```php
/**
 * Start autonomous trading session
 *
 * @param Request $request
 * @return JsonResponse
 */
public function startTrading(Request $request): JsonResponse
{
    // Implementation
}
```

### **JavaScript/Vue.js**
- Use ESLint with standard configuration
- Prefer const/let over var
- Use descriptive component names
- Follow Vue.js style guide

## 🧪 **Testing Guidelines**

### **Backend Tests**
```bash
cd backend
source env/bin/activate
python -m pytest tests/
```

### **Frontend Tests**
```bash
cd frontend
php artisan test
npm run test
```

### **Integration Tests**
```bash
./test_system.sh
```

## 📋 **Pull Request Process**

### **Before Submitting**
1. **Test locally**: Ensure all tests pass
2. **Update documentation**: If adding features, update relevant docs
3. **Check security**: No exposed API keys or secrets
4. **Verify functionality**: Test the complete user workflow

### **PR Checklist**
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 🚀 **Feature Development**

### **Adding New Trading Algorithms**
1. Create algorithm in `backend/algorithms/`
2. Add tests in `backend/tests/test_algorithms.py`
3. Update configuration in `backend/config.py`
4. Document in `API_REFERENCE.md`

### **Adding Frontend Features**
1. Create Vue component in `frontend/resources/js/Components/`
2. Add route in `frontend/routes/web.php`
3. Create controller method if needed
4. Update navigation and documentation

### **API Changes**
1. Update backend endpoint
2. Update frontend API calls
3. Document in `API_REFERENCE.md`
4. Add tests for new endpoints

## 🛡️ **Security Guidelines**

### **API Keys and Secrets**
- Never commit real API keys
- Use environment variables
- Provide example configurations
- Document security requirements

### **Input Validation**
- Validate all user inputs
- Sanitize data before database storage
- Use Laravel's validation features
- Implement rate limiting

### **Error Handling**
- Don't expose sensitive information in errors
- Log security events
- Use appropriate HTTP status codes

## 📊 **Performance Guidelines**

### **Backend Performance**
- Optimize database queries
- Use caching where appropriate
- Implement proper error handling
- Monitor API response times

### **Frontend Performance**
- Minimize API calls
- Use Vue.js reactivity efficiently
- Optimize bundle size
- Implement loading states

## 📚 **Documentation**

### **Code Documentation**
- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Keep comments up to date

### **User Documentation**
- Update user manual for new features
- Include screenshots where helpful
- Provide troubleshooting steps
- Maintain setup instructions

## 🐛 **Bug Reports**

### **Bug Report Template**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: 
- Python version:
- PHP version:
- Browser (if frontend):

## Additional Context
Any other context about the problem
```

## 💡 **Feature Requests**

### **Feature Request Template**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other ways to solve this problem

## Additional Context
Any other context or screenshots
```

## 🏆 **Recognition**

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Given credit in documentation

## 📞 **Getting Help**

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Report security issues privately

## 📄 **License**

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the Autonomous Trading Bot! 🤖💰