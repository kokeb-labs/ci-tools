// Seeded violation: main's only handler rethrows, so every exception escapes main.
namespace kv::rule_18_3_1::bad_rethrow {

inline void work() {}

}  // namespace kv::rule_18_3_1::bad_rethrow

int main() {
  try {
    kv::rule_18_3_1::bad_rethrow::work();
  } catch (...) {  // seeded: gcc
    throw;  // seeded: clang
  }
  return 0;
}
