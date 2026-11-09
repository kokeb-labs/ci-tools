// Seeded violation: a value that needs long long on a 32-bit target, written with a single L.
namespace kv::rule_5_13_6::bad {

long long big() { return 3000000000L; }  // long long on ILP32 targets  // seeded

}  // namespace kv::rule_5_13_6::bad
