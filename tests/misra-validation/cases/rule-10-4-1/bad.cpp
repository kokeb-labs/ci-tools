// Seeded violation: an asm declaration in C++ code.
namespace kv::rule_10_4_1::bad {

void barrier() {
  asm volatile("" ::: "memory");  // seeded
}

}  // namespace kv::rule_10_4_1::bad
