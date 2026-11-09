// Seeded violation: the standard integer type names, whose width depends on the platform.
namespace kv::rule_6_9_2::bad {

long widen(int narrow) {  // seeded
  unsigned short const small = 2;  // seeded
  return narrow + small;
}

}  // namespace kv::rule_6_9_2::bad
