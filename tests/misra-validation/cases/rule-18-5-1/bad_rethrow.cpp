// Seeded violation: a noexcept function rethrows from its handler.
namespace kv::rule_18_5_1::bad_rethrow {

void step();

void run() noexcept {
  try {
    step();
  } catch (...) {  // seeded: gcc
    throw;  // seeded: clang
  }
}

}  // namespace kv::rule_18_5_1::bad_rethrow
