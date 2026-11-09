// Seeded violation: the standard integer type names, whose width depends on the platform.
namespace kv::rule_6_9_2::bad {

long widen(int narrow) {
  unsigned short const small = 2;
  return narrow + small;
}

}  // namespace kv::rule_6_9_2::bad
