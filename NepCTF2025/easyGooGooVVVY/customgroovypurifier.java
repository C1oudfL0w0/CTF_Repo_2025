package org.example.expressinject.Test.Groovy;

import org.codehaus.groovy.ast.ClassNode;
import org.codehaus.groovy.ast.expr.Expression;
import org.codehaus.groovy.ast.expr.MethodCallExpression;
import org.codehaus.groovy.control.customizers.SecureASTCustomizer;

import java.lang.reflect.Method;
import java.util.*;

public class CustomGroovyPurifier extends SecureASTCustomizer {
    private static final Set<String> STRING_METHODS = new HashSet<>();
    private SecureASTCustomizer secureASTCustomizer = new SecureASTCustomizer();

    public SecureASTCustomizer CreateASTCustomizer() {

        secureASTCustomizer.addExpressionCheckers(expr -> {
            if (expr instanceof MethodCallExpression) {
                MethodCallExpression methodCall = (MethodCallExpression) expr;
                Expression objectExpr = methodCall.getObjectExpression();
                ClassNode type = objectExpr.getType();
                type.getClass();
                String typeName = type.getName();
                String methodName = methodCall.getMethodAsString();
                if (typeName.equals("java.lang.String")) {
                    if (STRING_METHODS.contains(methodName)) {
                        return true;
                    } else {
                        throw new SecurityException("Calling "+methodName+"  on "+ "String is not allowed");
                    }
                }

                if (methodName.equals("execute")) {
                        throw new SecurityException("Calling "+methodName+" on "+ "is not allowed");
                }
            }
            return true;
        });
        secureASTCustomizer.setClosuresAllowed(false);
        return secureASTCustomizer;
    }
    static {
        for (Method method : String.class.getDeclaredMethods()) {
            STRING_METHODS.add(method.getName());
        }
    }

}
