// Seeded violation: an empty throw expression outside a catch handler.
namespace kv::rule_18_1_2::bad {

void again() { throw; }  // seeded

}  // namespace kv::rule_18_1_2::bad
