// Seeded violation: main catches one type only, so anything else escapes.
namespace kv::rule_18_3_1::bad {

struct Fault {};

void work() {}

}  // namespace kv::rule_18_3_1::bad

int main() {
  try {  // seeded: clang
    kv::rule_18_3_1::bad::work();
  } catch (const kv::rule_18_3_1::bad::Fault&) {  // seeded: gcc
    return 1;
  }
  return 0;
}
