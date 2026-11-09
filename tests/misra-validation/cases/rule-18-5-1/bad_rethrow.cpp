// Seeded violation: a noexcept function rethrows from its handler.
namespace kv::rule_18_5_1::bad_rethrow {

void step();

void run() noexcept {
  try {
    step();
  } catch (...) {
    throw;
  }
}

}  // namespace kv::rule_18_5_1::bad_rethrow
