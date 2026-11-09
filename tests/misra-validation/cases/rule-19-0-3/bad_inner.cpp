// Seeded violation: an #include inside a namespace, after a declaration.
namespace kv::rule_19_0_3::bad_inner {

constexpr int kFirst = 1;

#include "kv_inner.inc"  // seeded

}  // namespace kv::rule_19_0_3::bad_inner
