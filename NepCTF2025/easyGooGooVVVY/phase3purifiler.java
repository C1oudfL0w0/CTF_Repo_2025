package org.example.expressinject.Test.Groovy;

import groovy.lang.Grab;
import groovy.transform.ASTTest;
import org.codehaus.groovy.ast.*;
import org.codehaus.groovy.classgen.GeneratorContext;
import org.codehaus.groovy.control.CompilationFailedException;
import org.codehaus.groovy.control.CompilationUnit;
import org.codehaus.groovy.control.CompilePhase;
import org.codehaus.groovy.control.SourceUnit;
import org.codehaus.groovy.control.customizers.CompilationCustomizer;

import java.lang.annotation.Annotation;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class Phase3Purifiler extends CompilationCustomizer {
    private static final List<String> BLOCKED_TRANSFORMS = Collections.unmodifiableList(Arrays.asList(
            "ASTTest",
            "Grab",
            "GrabConfig",
            "GrabExclude",
            "GrabResolver",
            "Grapes",
            "AnnotationCollector"
    ));

    public Phase3Purifiler() {
        super(CompilePhase.CONVERSION);
    }

    @Override
    public void call(SourceUnit source, GeneratorContext context, ClassNode classNode) throws CompilationFailedException {
        new RejectASTTransformsVisitor(source).visitClass(classNode);
    }

    @Override
    public void doPhaseOperation(CompilationUnit unit) throws CompilationFailedException {
        super.doPhaseOperation(unit);
    }

    @Override
    public boolean needSortedInput() {
        return super.needSortedInput();
    }


    private static class RejectASTTransformsVisitor extends ClassCodeVisitorSupport {
        private SourceUnit source;

        public RejectASTTransformsVisitor(SourceUnit source) {
            this.source = source;
        }

        @Override
        protected SourceUnit getSourceUnit() {
            return source;
        }

        @Override
        public void visitAnnotations(AnnotatedNode node) {
            for (AnnotationNode an : node.getAnnotations()) {
                for (String blockedAnnotation : BLOCKED_TRANSFORMS) {
                    if (an.getClassNode().getName().contains(blockedAnnotation)) {
                        throw new SecurityException("Annotation " + blockedAnnotation + " cannot be used in the sandbox.");
                    }
                }
            }
        }

        @Override
        public void visitImports(ModuleNode node) {
            if (node != null) {
                for (ImportNode importNode : node.getImports()) {
                    checkImportForBlockedAnnotation(importNode);
                }
                for (ImportNode importStaticNode : node.getStaticImports().values()) {
                    checkImportForBlockedAnnotation(importStaticNode);
                }
            }
        }

    }

    private static void checkImportForBlockedAnnotation(ImportNode node) {
        if (node != null && node.getType() != null) {
            for (String blockedAnnotation : BLOCKED_TRANSFORMS) {
                if (node.getType().getName().contains(blockedAnnotation)) {
                    throw new SecurityException("Annotation " + node.getType().getName() + " cannot be used in the sandbox.");
                }
            }
        }
    }
}

